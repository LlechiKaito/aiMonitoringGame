from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Objectsモデルの詳細
class Object(BaseModel):
    id: int  # レスポンスモデルなので常にIDが存在
    name: str
    summary: str
    description: str
    photos: Optional[str] = "[]"  # JSON文字列として多次元配列を保存

# 作成のリクエストパラメーター
class ObjectCreate(BaseModel):
    name: str
    summary: str
    description: str
    photos: Optional[str] = "[]"  # JSON文字列として多次元配列を保存

# 更新のリクエストパラメーター
class ObjectUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    photos: Optional[str] = None  # JSON文字列として多次元配列を保存

# 取得のリクエストパラメーター
class ObjectQuery(BaseModel):
    name: Optional[str] = None
    limit: Optional[int] = 10 