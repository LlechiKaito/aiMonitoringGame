import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# データベース関連のインポート
from utils.database import create_tables
# すべてのデータベースモデルをインポート（テーブル作成のため）
from utils.db_models import ObjectDB, MemoryDB, SummaryDB

# memoriesモジュールをインポート
from memories import router as memories_router
# objectsモジュールをインポート
from objects import router as objects_router
# summariesモジュールをインポート
from summaries import router as summaries_router

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="AI Monitoring Game API",
    description="AIモニタリングゲーム用のバックエンドAPI",
    version="1.0.0"
)

# CORSミドルウェアを追加（フロントエンドとの通信を許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# アプリケーション起動時にデータベースを初期化
@app.on_event("startup")
async def startup_event():
    # データベーステーブルを作成
    create_tables()

# memoriesルーターを追加
app.include_router(memories_router)
# objectsルーターを追加
app.include_router(objects_router)
# summariesルーターを追加
app.include_router(summaries_router)

# サーバー起動用のメイン関数
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 