from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Memoriesモデルの詳細
class Memory(BaseModel):
    id: int  # レスポンスモデルなので常にIDが存在
    object_id: int
    content: str
    importance: int = Field(default=5, description="重要度（1-9の整数値）")
    timestamp: datetime  # 作成時に必ず設定される
    last_accessed: datetime  # 作成・取得時に必ず設定される

# 作成のリクエストパラメーター
class MemoryCreate(BaseModel):
    object_id: int
    content: str
    importance: int = Field(default=5, description="重要度（1-9の整数値）")

# 更新のリクエストパラメーター
class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    importance: Optional[int] = Field(default=None, description="重要度（1-9の整数値）")

# 取得のリクエストパラメーター
class MemoryQuery(BaseModel):
    object_id: Optional[int] = None
    query: Optional[str] = None
    limit: Optional[int] = 5