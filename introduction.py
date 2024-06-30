# 소개페이지.
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
import aiofiles
from motor.motor_asyncio import AsyncIOMotorClient
import os  # os 모듈을 가져와서 환경 변수를 읽기 위함
from auth import get_user_role, get_current_username

# FastAPI의 APIRouter 객체 생성, 이를 통해 라우트를 그룹화
router = APIRouter()

# MongoDB 클라이언트를 설정하고 데이터베이스 연결
client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/kustii"))
db = client["board"]

# Pydantic 모델 정의, 요청 데이터 검증을 위함
class IntroductionPost(BaseModel):
    title: str  # 제목
    content: str  # 최대 3000자 내용
    image: str = None # 이미지 파일 경로

# type : 게시글 종류
#   hello : 인사말
#   intro : KUSTII소개
#   organization : 조직도

@router.post("/update/{type}", response_model=IntroductionPost, dependencies=[Depends(get_current_username)])
async def update_post(
        type: str, 
        title: str = Form(...), 
        content: str = Form(...), 
        image: UploadFile = File(None), 
        username: str = Depends(get_user_role)
        ):
    if username != "superadmin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    post_dict = {"title": title, "content": content}    
    if image:  # 이미지 파일이 있는 경우
        file_location = f"images/{image.filename}"  # 이미지 파일 경로 설정
        async with aiofiles.open(file_location, 'wb') as out_file:  # 비동기 파일 쓰기
            content = await image.read()  # 이미지 파일 읽기
            await out_file.write(content)  # 이미지 파일 쓰기
        post_dict['image'] = file_location  # 딕셔너리에 이미지 파일 경로 추가
    
    # 문서 업데이트 (upsert를 통해 문서가 없으면 삽입)
    result = await db[type].update_one(
        {},  # 조건을 비워두어 컬렉션의 첫 번째 문서를 찾음
        {"$set": post_dict},  # 문서를 업데이트
        upsert=True  # 문서가 없으면 새 문서 삽입
    )
    # 업데이트된 문서 또는 삽입된 문서를 반환
    updated_post = await db[type].find_one({})
    updated_post["_id"] = str(updated_post["_id"])  # ObjectId를 문자열로 변환    
    return updated_post  # 생성된 게시물 반환

# 게시물 조회 엔드포인트, GET 요청을 처리
@router.get("/{type}", response_model=IntroductionPost)
async def get_post(type: str):
    post = await db[type].find_one()  # 첫 번째 게시물 조회
    if post:
        post["_id"] = str(post["_id"])  # ObjectId를 문자열로 변환
        return post
    else:
        raise HTTPException(status_code=404, detail="Post not found")