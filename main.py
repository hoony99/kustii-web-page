from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
import uvicorn
from auth import router as login_router 
from introduction import router as introduction_router
from main_business import router as main_buiness_router
from notice import router as notice_router
from media_center import router as media_center_router
app = FastAPI()

app.include_router(login_router, tags=["login"])
app.include_router(introduction_router, prefix="/introduction", tags=["introduction"])
app.include_router(main_buiness_router, prefix="/mainbuiness", tags=["main_buiness"])
app.include_router(notice_router, prefix="/notice", tags=["notice"])
app.include_router(media_center_router, prefix="/mediacenter", tags=["media_center"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)