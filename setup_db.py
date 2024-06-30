# setup_db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def setup_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/kustii"))
    db = client["board"]

    # 인사말 게시판 기본 데이터 삽입
    hello = {
        "title": "인사말 게시판 제목",
        "content": "인사말 게시판 본문",
        "image_url": None
    }
    await db["hello"].update_one({}, {"$setOnInsert": hello}, upsert=True)

    intro = {
        "title": "KUSTII 게시판 제목",
        "content": "KUSTII 게시판 본문",
        "image_url": None
    }
    await db["intro"].update_one({}, {"$setOnInsert": intro}, upsert=True)

    organization = {
        "title": "조직도 게시판 제목",
        "content": "조직도 게시판 본문",
        "image_url": None
    }
    await db["organization"].update_one({}, {"$setOnInsert": organization}, upsert=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_db())
