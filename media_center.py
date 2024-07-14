# 미디어 게시판
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
import aiofiles
from motor.motor_asyncio import AsyncIOMotorClient
import os
from auth import get_user_role, get_current_username
import requests
from PIL import Image
from io import BytesIO

# FastAPI의 APIRouter 객체 생성, 이를 통해 라우트를 그룹화
router = APIRouter()

# MongoDB 클라이언트를 설정하고 데이터베이스 연결
client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/kustii"))
db = client["board"]

# Pydantic 모델 정의, 요청 데이터 검증을 위함
class MediaPost(BaseModel):
    title: str  # 제목
    url: str  # URL 주소
    thumbnail: Optional[str] = None  # 썸네일 이미지 경로
    files: Optional[List[str]] = None  # 파일 경로 리스트

################################################################################
#################################미디어 게시판##################################
#################################Create test O##################################
#################################Update test ##################################
#################################Delete test ##################################
#################################Read   test ##################################
#################################Comment test #################################
################################################################################
# URL에서 이미지를 다운로드하여 저장하는 함수
async def save_image_from_url(url: str, save_path: str):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image.save(save_path)

# 게시물 create
@router.post("/create/{type}", response_model=MediaPost, dependencies=[Depends(get_current_username)])
async def create_media_post(
        type: str,
        title: str = Form(...), 
        url: str = Form(...), 
        files: List[UploadFile] = File(None), 
        username: str = Depends(get_user_role)
    ):
    if username != "superadmin" and username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if type != "media":
        raise HTTPException(status_code=400, detail="Invalid type")
    
    post_dict = {"title": title, "url": url, "files": [], "thumbnail": None}
    
    if files:  # 파일이 있는 경우
        for file in files:
            file_location = f"files/{file.filename}"  # 파일 경로 설정
            async with aiofiles.open(file_location, 'wb') as out_file:  # 비동기 파일 쓰기
                file_content = await file.read()  # 파일 읽기
                await out_file.write(file_content)  # 파일 쓰기
            post_dict['files'].append(file_location)  # 딕셔너리에 파일 경로 추가
            post_dict['thumbnail'] = file_location  # 썸네일로 사용
    
    if not post_dict['thumbnail']:  # 썸네일이 없을 경우 URL에서 이미지 다운로드
        thumbnail_path = f"files/{title}_thumbnail.jpg"
        await save_image_from_url(url, thumbnail_path)
        post_dict['thumbnail'] = thumbnail_path
    
    result = await db[type].insert_one(post_dict)  # MongoDB에 게시물 삽입
    post_dict["_id"] = str(result.inserted_id)  # 삽입된 문서의 ID를 딕셔너리에 추가    
    return post_dict  # 생성된 게시물 반환

# 게시물 update
@router.put("/update/{type}/{post_id}", response_model=MediaPost, dependencies=[Depends(get_current_username)])
async def update_media_post(
        type: str,
        post_id: str,
        title: str = Form(...), 
        url: str = Form(...), 
        files: List[UploadFile] = File(None), 
        username: str = Depends(get_user_role)
    ):
    if username != "superadmin" and username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if type != "media":
        raise HTTPException(status_code=400, detail="Invalid type")

    post_dict = {"title": title, "url": url, "files": [], "thumbnail": None}
    
    if files:  # 파일이 있는 경우
        for file in files:
            file_location = f"files/{file.filename}"  # 파일 경로 설정
            async with aiofiles.open(file_location, 'wb') as out_file:  # 비동기 파일 쓰기
                file_content = await file.read()  # 파일 읽기
                await out_file.write(file_content)  # 파일 쓰기
            post_dict['files'].append(file_location)  # 딕셔너리에 파일 경로 추가
            post_dict['thumbnail'] = file_location  # 썸네일로 사용
    
    if not post_dict['thumbnail']:  # 썸네일이 없을 경우 URL에서 이미지 다운로드
        thumbnail_path = f"files/{title}_thumbnail.jpg"
        await save_image_from_url(url, thumbnail_path)
        post_dict['thumbnail'] = thumbnail_path
    
    # 문서 업데이트
    result = await db[type].update_one(
        {"_id": ObjectId(post_id)},  # 특정 문서 조건
        {"$set": post_dict}  # 문서를 업데이트
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    updated_post = await db[type].find_one({"_id": ObjectId(post_id)})
    updated_post["_id"] = str(updated_post["_id"])  # ObjectId를 문자열로 변환    
    return updated_post  # 업데이트된 게시물 반환

# 게시물 delete
@router.delete("/delete/{type}/{post_id}", response_model=dict, dependencies=[Depends(get_current_username)])
async def delete_media_post(
        type: str, 
        post_id: str, 
        username: str = Depends(get_user_role)
        ):
    if username != "superadmin" and username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if type != "media":
        raise HTTPException(status_code=400, detail="Invalid type")

    result = await db[type].delete_one({"_id": ObjectId(post_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")    
    return {"message": "Deleted successfully"}

# 게시물 read
@router.get("/{type}/{post_id}", response_model=MediaPost)
async def get_media_post(type: str, post_id: str):
    if type != "media":
        raise HTTPException(status_code=400, detail="Invalid type")
    
    post = await db[type].find_one({"_id": ObjectId(post_id)})  # 특정 게시물 조회
    if post:
        post["_id"] = str(post["_id"])  # ObjectId를 문자열로 변환
        return post
    else:
        raise HTTPException(status_code=404, detail="Post not found")