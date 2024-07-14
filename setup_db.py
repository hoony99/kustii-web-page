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

    media = {
        "title": "미디어센터 제목",
        "url": "미디어센터 URL",
        "files": None
    }
    await db["media"].update_one({}, {"$setOnInsert": media}, upsert=True)

    forum = {
        "title": "포럼 제목",
        "content": "포럼 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["forum"].update_one({}, {"$setOnInsert": forum}, upsert=True)

    assist = {
        "title": "assist 제목",
        "content": "assist 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["assist"].update_one({}, {"$setOnInsert": assist}, upsert=True)

    stemtraining = {
        "title": "stemtraining 제목",
        "content": "stemtraining 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["stemtraining"].update_one({}, {"$setOnInsert": stemtraining}, upsert=True)

    steducation = {
        "title": "steducation 제목",
        "content": "steducation 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["steducation"].update_one({}, {"$setOnInsert": steducation}, upsert=True)

    essay = {
        "title": "essay 제목",
        "content": "essay 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["essay"].update_one({}, {"$setOnInsert": essay}, upsert=True)

    news = {
        "title": "news 제목",
        "content": "news 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["news"].update_one({}, {"$setOnInsert": news}, upsert=True)

    notice = {
        "title": "notice 제목",
        "content": "notice 본문",
        "files": [],
        "comments": [],
        "views": 0
    }
    await db["notice"].update_one({}, {"$setOnInsert": notice}, upsert=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_db())
