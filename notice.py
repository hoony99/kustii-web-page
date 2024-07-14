# 공지사항
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
class NoticePost(BaseModel):
    title: str  # 제목
    content: str  # 최대 3000자 내용
    files: Optional[List[str]] = None  # 파일 경로 리스트
    comments: Optional[List['CommentInDB']] = []
    views: int = 0  # 조회수 필드 추가

class Comment(BaseModel):
    user: str
    content: str
    is_admin: bool = False
    replies: Optional[List['CommentInDB']] = []
    id: Optional[str]

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None

class CommentInDB(Comment):
    id: Optional[str]

# 타입을 확인하는 부분
types = ["news", "notice"]  
# type : 게시글 종류
#   news : 한미과기동맹포럼
#   notice : 기술.인력.정보.판매.협력 알선&지원
################################################################################
#################################공지사항 게시판#################################
#################################Create test O##################################
#################################Update test ##################################
#################################Delete test ##################################
#################################Read   test ##################################
#################################Comment test #################################
################################################################################

# 게시물 create
@router.post("/create/{type}", response_model=NoticePost, dependencies=[Depends(get_current_username)])
async def create_forum_post(
        type: str,
        title: str = Form(...), 
        content: str = Form(...), 
        files: List[UploadFile] = File(None), 
        username: str = Depends(get_user_role)
    ):
    if username != "superadmin" and username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if type not in types:
        raise HTTPException(status_code=400, detail="Invalid type")
    
    post_dict = {"title": title, "content": content, "files": [], "comments": [], "views": 0}
    
    if files:  # 파일이 있는 경우
        for file in files:
            file_location = f"files/{file.filename}"  # 파일 경로 설정
            async with aiofiles.open(file_location, 'wb') as out_file:  # 비동기 파일 쓰기
                file_content = await file.read()  # 파일 읽기
                await out_file.write(file_content)  # 파일 쓰기
            post_dict['files'].append(file_location)  # 딕셔너리에 파일 경로 추가
    
    result = await db[type].insert_one(post_dict)  # MongoDB에 게시물 삽입
    post_dict["_id"] = str(result.inserted_id)  # 삽입된 문서의 ID를 딕셔너리에 추가    
    return post_dict  # 생성된 게시물 반환

# 게시물 update
@router.put("/update/{type}/{post_id}", response_model=NoticePost, dependencies=[Depends(get_current_username)])
async def update_forum_post(
        type: str,
        post_id: str,
        title: str = Form(...), 
        content: str = Form(...), 
        files: List[UploadFile] = File(None), 
        username: str = Depends(get_user_role)
    ):
    if username != "superadmin" and username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    post_dict = {"title": title, "content": content, "files": []}
    
    if files:  # 파일이 있는 경우
        for file in files:
            file_location = f"files/{file.filename}"  # 파일 경로 설정
            async with aiofiles.open(file_location, 'wb') as out_file:  # 비동기 파일 쓰기
                file_content = await file.read()  # 파일 읽기
                await out_file.write(file_content)  # 파일 쓰기
            post_dict['files'].append(file_location)  # 딕셔너리에 파일 경로 추가
    
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
async def delete_forum_post(
        type: str, 
        post_id: str, 
        username: str = Depends(get_user_role)
        ):
    if username != "superadmin" and username != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db[type].delete_one({"_id": ObjectId(post_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")    
    return {"message": "Deleted successfully"}

# 게시물 read
@router.get("/{type}/{post_id}", response_model=NoticePost)
async def get_forum_post(type: str, post_id: str):
    if type not in types:
        raise HTTPException(status_code=400, detail="Invalid type")
    
    # 조회수 증가
    await db[type].update_one({"_id": ObjectId(post_id)}, {"$inc": {"views": 1}})
        
    post = await db[type].find_one({"_id": ObjectId(post_id)})  # 특정 게시물 조회
    if post:
        post["_id"] = str(post["_id"])  # ObjectId를 문자열로 변환
        return post
    else:
        raise HTTPException(status_code=404, detail="Post not found")
    
# FAQ 게시판 제작












################################################################################
#############################공지사항 게시판 댓글기능#############################
################################################################################

# 댓글 추가
@router.post("/{type}/{post_id}/comments", response_model=CommentInDB)
async def add_comment(
    type: str,
    post_id: str,
    comment: CommentCreate,
    username: str = Depends(get_current_username),
    user_role: str = Depends(get_user_role)
):
    is_admin = user_role in ["admin", "superadmin"]
    comment_dict = {
        "user": username,
        "content": comment.content,
        "is_admin": is_admin,
        "replies": []
    }
    
    post = await db[type].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if comment.parent_id:
        parent_comment = await db["comments"].find_one({"_id": ObjectId(comment.parent_id)})
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        await db["comments"].update_one(
            {"_id": ObjectId(comment.parent_id)},
            {"$push": {"replies": comment_dict}}
        )
    else:
        result = await db["comments"].insert_one(comment_dict)
        comment_dict["_id"] = str(result.inserted_id)
        
        await db[type].update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment_dict}}
        )
    
    return comment_dict

# 댓글 조회
@router.get("/{type}/{post_id}/comments", response_model=List[CommentInDB])
async def get_comments(type: str, post_id: str):
    if type not in types:
        raise HTTPException(status_code=400, detail="Invalid type")
        
    post = await db[type].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.get("comments", [])

# 댓글 삭제
@router.delete("/{type}/{post_id}/comments/{comment_id}", response_model=dict, dependencies=[Depends(get_current_username)])
async def delete_comment(
    type: str,
    post_id: str,
    comment_id: str,
    username: str = Depends(get_current_username),
    user_role: str = Depends(get_user_role)
):
    if user_role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    post = await db[type].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    result = await db["comments"].delete_one({"_id": ObjectId(comment_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    await db[type].update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"_id": ObjectId(comment_id)}}}
    )
    
    return {"message": "Comment deleted successfully"}