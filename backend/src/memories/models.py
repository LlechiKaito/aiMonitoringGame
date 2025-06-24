from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Memoriesモデルの詳細
class Memory(BaseModel):
    id: Optional[int] = None
    object_id: int
    content: str
    importance: float = 0.5
    timestamp: Optional[datetime] = None
    last_accessed: Optional[datetime] = None

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
    min_importance: Optional[float] = None
    limit: Optional[int] = 10