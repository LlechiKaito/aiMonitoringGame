from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Memoriesモデルの詳細
class Memory(BaseModel):
    id: int  # レスポンスモデルなので常にIDが存在
    object_id: int
    content: str
    importance: float = 0.5
    timestamp: datetime  # 作成時に必ず設定される
    last_accessed: datetime  # 作成・取得時に必ず設定される

# 作成のリクエストパラメーター
class MemoryCreate(BaseModel):
    object_id: int
    content: str
    importance: float = 0.5

# 更新のリクエストパラメーター
class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    importance: Optional[float] = None

# 取得のリクエストパラメーター
class MemoryQuery(BaseModel):
    object_id: int
    limit: Optional[int] = 10