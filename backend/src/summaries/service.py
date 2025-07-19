from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Summary, SummaryCreate, SummaryUpdate, SummaryQuery
from utils.db_models import SummaryDB, ObjectDB
import pytz

class SummaryService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_string_field(self, field_name: str, value: str) -> None:
        """文字列フィールドが1文字以上であることを確認"""
        if not value or len(value.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be at least 1 character long"
            )

    # レコードの作成
    def create_summary(self, summary_data: SummaryCreate) -> Summary:
        # 文字列フィールドのバリデーション
        self._validate_string_field("Key features", summary_data.key_features)
        self._validate_string_field("Current daily tasks", summary_data.current_daily_tasks)
        self._validate_string_field("Recent progress feelings", summary_data.recent_progress_feelings)
        
        # 外部キー（object_id）の存在確認
        existing_object = self.db.query(ObjectDB).filter(ObjectDB.id == summary_data.object_id).first()
        if not existing_object:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {summary_data.object_id} not found"
            )
        
        db_summary = SummaryDB(
            object_id=summary_data.object_id,
            key_features=summary_data.key_features,
            current_daily_tasks=summary_data.current_daily_tasks,
            recent_progress_feelings=summary_data.recent_progress_feelings,
            created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        
        self.db.add(db_summary)
        self.db.commit()
        self.db.refresh(db_summary)
        
        return Summary(
            id=db_summary.id,
            object_id=db_summary.object_id,
            key_features=db_summary.key_features,
            current_daily_tasks=db_summary.current_daily_tasks,
            recent_progress_feelings=db_summary.recent_progress_feelings,
            created_at=db_summary.created_at
        )

    # 単一レコードの取得
    def get_summary(self, summary_id: int) -> Summary:
        db_summary = self.db.query(SummaryDB).filter(SummaryDB.id == summary_id).first()
        
        if not db_summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary with id {summary_id} not found"
            )
        
        return Summary(
            id=db_summary.id,
            object_id=db_summary.object_id,
            key_features=db_summary.key_features,
            current_daily_tasks=db_summary.current_daily_tasks,
            recent_progress_feelings=db_summary.recent_progress_feelings,
            created_at=db_summary.created_at
        )

    # レコードの取得（複数）
    def get_summaries(self, query: SummaryQuery) -> List[Summary]:
        db_query = self.db.query(SummaryDB).filter(SummaryDB.object_id == query.object_id)
        
        # 作成日時でソート（新しい順）
        db_query = db_query.order_by(SummaryDB.created_at.desc())
        
        if query.limit:
            db_query = db_query.limit(query.limit)
        
        db_summaries = db_query.all()
        
        # 結果が空の場合は404エラーを発生
        if not db_summaries:
            raise HTTPException(
                status_code=404,
                detail=f"No summaries found for object_id {query.object_id}"
            )
        
        return [
            Summary(
                id=db_summary.id,
                object_id=db_summary.object_id,
                key_features=db_summary.key_features,
                current_daily_tasks=db_summary.current_daily_tasks,
                recent_progress_feelings=db_summary.recent_progress_feelings,
                created_at=db_summary.created_at
            )
            for db_summary in db_summaries
        ]

    # レコードの更新
    def update_summary(self, summary_id: int, update_data: SummaryUpdate) -> Summary:
        db_summary = self.db.query(SummaryDB).filter(SummaryDB.id == summary_id).first()
        
        if not db_summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary with id {summary_id} not found"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 空文字列やNoneのフィールドを除外
        valid_update_dict = {}
        for key, value in update_dict.items():
            if key in ['key_features', 'current_daily_tasks', 'recent_progress_feelings']:
                # 文字列フィールドの場合は空文字列や空白のみの場合は除外
                if value is not None and len(str(value).strip()) > 0:
                    field_name_map = {
                        'key_features': 'Key features',
                        'current_daily_tasks': 'Current daily tasks',
                        'recent_progress_feelings': 'Recent progress feelings'
                    }
                    self._validate_string_field(field_name_map[key], value)
                    valid_update_dict[key] = value
        
        # 更新するフィールドがない場合は400エラー
        if not valid_update_dict:
            raise HTTPException(
                status_code=400,
                detail="No valid fields to update. All provided fields are empty or invalid."
            )
        
        for key, value in valid_update_dict.items():
            setattr(db_summary, key, value)
        
        self.db.commit()
        
        return Summary(
            id=db_summary.id,
            object_id=db_summary.object_id,
            key_features=db_summary.key_features,
            current_daily_tasks=db_summary.current_daily_tasks,
            recent_progress_feelings=db_summary.recent_progress_feelings,
            created_at=db_summary.created_at
        )

    # レコードの削除
    def delete_summary(self, summary_id: int) -> None:
        db_summary = self.db.query(SummaryDB).filter(SummaryDB.id == summary_id).first()
        
        if not db_summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary with id {summary_id} not found"
            )
        
        self.db.delete(db_summary)
        self.db.commit()

# サービスのファクトリー関数
def get_summary_service(db: Session) -> SummaryService:
    return SummaryService(db) 