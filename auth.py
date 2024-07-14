################################################################################
###################################로그인 기능###################################
################################API TEST COMPLETE###############################
################################################################################

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

router = APIRouter()
security = HTTPBasic()

# 관리자 계정
admin_accounts = {
    "superadmin": os.getenv("SUPERADMIN_PASSWORD"),
    "admin": os.getenv("ADMIN_PASSWORD")
}

# 권한 확인 함수
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username in admin_accounts and admin_accounts[credentials.username] == credentials.password:
        return credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

# 사용자 역할을 반환하는 함수
def get_user_role(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username in admin_accounts and admin_accounts[credentials.username] == credentials.password:
        return credentials.username
    else:
        return "user"

# 로그인 엔드포인트
@router.post("/login")
async def login(
        username: str = Form(...), 
        password: str = Form(...)
    ):
    if username in admin_accounts and admin_accounts[username] == password:
        return JSONResponse(content={"message": "Login successful", "role": username})
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
