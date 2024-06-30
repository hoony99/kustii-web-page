# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# 관리자 계정
admin_accounts = {
    "superadmin": "0000",
    "admin": "1234"
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
