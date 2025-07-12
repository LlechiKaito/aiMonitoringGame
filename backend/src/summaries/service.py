from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Summary, SummaryCreate, SummaryUpdate, SummaryQuery
from utils.db_models import SummaryDB, ObjectDB

class SummaryService:
    def __init__(self, db: Session):
        self.db = db

    # レコードの作成
    def create_summary(self, summary_data: SummaryCreate) -> Summary:
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
            created_at=datetime.now()
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
    def get_summary(self, summary_id: int) -> Optional[Summary]:
        db_summary = self.db.query(SummaryDB).filter(SummaryDB.id == summary_id).first()
        
        if db_summary:
            return Summary(
                id=db_summary.id,
                object_id=db_summary.object_id,
                key_features=db_summary.key_features,
                current_daily_tasks=db_summary.current_daily_tasks,
                recent_progress_feelings=db_summary.recent_progress_feelings,
                created_at=db_summary.created_at
            )
        return None

    # レコードの取得（複数）
    def get_summaries(self, query: SummaryQuery) -> List[Summary]:
        db_query = self.db.query(SummaryDB).filter(SummaryDB.object_id == query.object_id)
        
        # 作成日時でソート（新しい順）
        db_query = db_query.order_by(SummaryDB.created_at.desc())
        
        if query.limit:
            db_query = db_query.limit(query.limit)
        
        db_summaries = db_query.all()
        
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
    def update_summary(self, summary_id: int, update_data: SummaryUpdate) -> Optional[Summary]:
        db_summary = self.db.query(SummaryDB).filter(SummaryDB.id == summary_id).first()
        
        if db_summary:
            update_dict = update_data.dict(exclude_unset=True)
            
            for key, value in update_dict.items():
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
        return None

    # レコードの削除
    def delete_summary(self, summary_id: int) -> bool:
        db_summary = self.db.query(SummaryDB).filter(SummaryDB.id == summary_id).first()
        
        if db_summary:
            self.db.delete(db_summary)
            self.db.commit()
            return True
        return False

# サービスのファクトリー関数
def get_summary_service(db: Session) -> SummaryService:
    return SummaryService(db) 