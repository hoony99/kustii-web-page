from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

from auth import get_current_username 
from introduction import router as introduction_router
from main_business import router as main_buiness_router

app = FastAPI()

app.include_router(introduction_router, prefix="/introduction", tags=["introduction"])
app.include_router(main_buiness_router, prefix="/mainbuiness", tags=["main_buiness"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
