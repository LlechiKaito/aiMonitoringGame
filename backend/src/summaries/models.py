from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Summariesモデルの詳細
class Summary(BaseModel):
    id: int  # レスポンスモデルなので常にIDが存在
    object_id: int
    key_features: str
    current_daily_tasks: str
    recent_progress_feelings: str
    created_at: datetime  # 作成時に必ず設定される

# 作成のリクエストパラメーター
class SummaryCreate(BaseModel):
    object_id: int
    key_features: str
    current_daily_tasks: str
    recent_progress_feelings: str

# 更新のリクエストパラメーター
class SummaryUpdate(BaseModel):
    key_features: Optional[str] = None
    current_daily_tasks: Optional[str] = None
    recent_progress_feelings: Optional[str] = None

# 取得のリクエストパラメーター
class SummaryQuery(BaseModel):
    object_id: int
    limit: Optional[int] = 10 