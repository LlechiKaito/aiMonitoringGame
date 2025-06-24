from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Objectsモデルの詳細
class Object(BaseModel):
    id: Optional[int] = None
    name: str
    summary: str
    description: str

# 作成のリクエストパラメーター
class ObjectCreate(BaseModel):
    name: str
    summary: str
    description: str

# 更新のリクエストパラメーター
class ObjectUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None

# 取得のリクエストパラメーター
class ObjectQuery(BaseModel):
    name: Optional[str] = None
    limit: Optional[int] = 10 