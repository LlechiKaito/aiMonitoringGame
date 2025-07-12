from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Object, ObjectCreate, ObjectUpdate, ObjectQuery
from utils.db_models import ObjectDB, MemoryDB, SummaryDB
import json

class ObjectService:
    def __init__(self, db: Session):
        self.db = db

    # レコードの作成
    def create_object(self, object_data: ObjectCreate) -> Object:
        db_object = ObjectDB(
            name=object_data.name,
            summary=object_data.summary,
            description=object_data.description,
            photos=object_data.photos
        )
        
        self.db.add(db_object)
        self.db.commit()
        self.db.refresh(db_object)
        
        return Object(
            id=db_object.id,
            name=db_object.name,
            summary=db_object.summary,
            description=db_object.description,
            photos=db_object.photos
        )

    # 単一レコードの取得
    def get_object(self, object_id: int) -> Optional[Object]:
        db_object = self.db.query(ObjectDB).filter(ObjectDB.id == object_id).first()
        
        if db_object:
            return Object(
                id=db_object.id,
                name=db_object.name,
                summary=db_object.summary,
                description=db_object.description,
                photos=db_object.photos
            )
        return None

    # レコードの取得（複数）
    def get_objects(self, query: ObjectQuery) -> List[Object]:
        db_query = self.db.query(ObjectDB)
        
        if query.name:
            db_query = db_query.filter(ObjectDB.name.ilike(f"%{query.name}%"))
        
        # IDでソート（新しい順）
        db_query = db_query.order_by(ObjectDB.id.desc())
        
        if query.limit:
            db_query = db_query.limit(query.limit)
        
        db_objects = db_query.all()
        
        return [
            Object(
                id=db_object.id,
                name=db_object.name,
                summary=db_object.summary,
                description=db_object.description,
                photos=db_object.photos
            )
            for db_object in db_objects
        ]

    # レコードの更新
    def update_object(self, object_id: int, update_data: ObjectUpdate) -> Optional[Object]:
        db_object = self.db.query(ObjectDB).filter(ObjectDB.id == object_id).first()
        
        if db_object:
            update_dict = update_data.dict(exclude_unset=True)
            
            for key, value in update_dict.items():
                setattr(db_object, key, value)
            
            self.db.commit()
            
            return Object(
                id=db_object.id,
                name=db_object.name,
                summary=db_object.summary,
                description=db_object.description,
                photos=db_object.photos
            )
        return None

    # レコードの削除
    def delete_object(self, object_id: int) -> bool:
        db_object = self.db.query(ObjectDB).filter(ObjectDB.id == object_id).first()
        
        if db_object:
            self.db.delete(db_object)
            self.db.commit()
            return True
        return False

    # オブジェクトに関連するメモリを取得
    def get_object_memories(self, object_id: int, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """オブジェクトに関連するメモリを取得"""
        
        db_query = self.db.query(MemoryDB).filter(MemoryDB.object_id == object_id)
        db_query = db_query.order_by(MemoryDB.importance.desc(), MemoryDB.last_accessed.desc())
        
        if limit:
            db_query = db_query.limit(limit)
        
        memories = db_query.all()
        return [
            {
                "id": memory.id,
                "object_id": memory.object_id,
                "content": memory.content,
                "importance": memory.importance,
                "timestamp": memory.timestamp,
                "last_accessed": memory.last_accessed
            }
            for memory in memories
        ]

    # オブジェクトに関連するサマリーを取得
    def get_object_summaries(self, object_id: int, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """オブジェクトに関連するサマリーを取得"""
        
        db_query = self.db.query(SummaryDB).filter(SummaryDB.object_id == object_id)
        db_query = db_query.order_by(SummaryDB.created_at.desc())
        
        if limit:
            db_query = db_query.limit(limit)
        
        summaries = db_query.all()
        return [
            {
                "id": summary.id,
                "object_id": summary.object_id,
                "key_features": summary.key_features,
                "current_daily_tasks": summary.current_daily_tasks,
                "recent_progress_feelings": summary.recent_progress_feelings,
                "created_at": summary.created_at
            }
            for summary in summaries
        ]

    # オブジェクトの詳細情報を取得（メモリとサマリーを含む）
    def get_object_details(self, object_id: int, memory_limit: Optional[int] = 10, summary_limit: Optional[int] = 10) -> Optional[Dict[str, Any]]:
        """オブジェクトの詳細情報を取得（メモリとサマリーを含む）"""
        obj = self.get_object(object_id)
        if not obj:
            return None
        
        object_dict = obj.dict()
        object_dict["memories"] = self.get_object_memories(object_id, memory_limit)
        object_dict["summaries"] = self.get_object_summaries(object_id, summary_limit)
        
        return object_dict

# サービスのファクトリー関数
def get_object_service(db: Session) -> ObjectService:
    return ObjectService(db) 