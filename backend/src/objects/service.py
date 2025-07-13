from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Object, ObjectCreate, ObjectUpdate, ObjectQuery
from utils.db_models import ObjectDB, MemoryDB, SummaryDB
import json
import pytz

class ObjectService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_string_field(self, field_name: str, value: str) -> None:
        """文字列フィールドが1文字以上であることを確認"""
        if not value or len(value.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be at least 1 character long"
            )

    def _validate_photos_field(self, photos: str) -> None:
        """photosフィールドが有効なJSON文字列であることを確認"""
        # JSON形式の検証
        try:
            json.loads(photos)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Photos must be valid JSON format"
            )

    # レコードの作成
    def create_object(self, object_data: ObjectCreate) -> Object:
        # 文字列フィールドのバリデーション
        self._validate_string_field("Name", object_data.name)
        self._validate_string_field("Summary", object_data.summary)
        self._validate_string_field("Description", object_data.description)
        
        # photosフィールドのバリデーション（JSON形式のみ）
        if object_data.photos is not None and object_data.photos.strip():
            self._validate_photos_field(object_data.photos)
        
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
    def get_object(self, object_id: int) -> Object:
        db_object = self.db.query(ObjectDB).filter(ObjectDB.id == object_id).first()
        
        if not db_object:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {object_id} not found"
            )
        
        return Object(
            id=db_object.id,
            name=db_object.name,
            summary=db_object.summary,
            description=db_object.description,
            photos=db_object.photos
        )

    # レコードの取得（複数）
    def get_objects(self, query: ObjectQuery) -> List[Object]:
        db_query = self.db.query(ObjectDB)
        
        # query.nameがNoneまたは空文字列の場合はバリデーションエラー
        if not query.name or not query.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Search name must be at least 1 character long"
            )
        
        db_query = db_query.filter(ObjectDB.name.ilike(f"%{query.name}%"))
        
        # IDでソート（新しい順）要検討
        db_query = db_query.order_by(ObjectDB.id.desc())
        
        if query.limit:
            db_query = db_query.limit(query.limit)
        
        db_objects = db_query.all()
        
        # 結果が空の場合は404エラーを発生
        if not db_objects:
            raise HTTPException(
                status_code=404,
                detail=f"No objects found with name containing '{query.name}'"
            )
        
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
    def update_object(self, object_id: int, update_data: ObjectUpdate) -> Object:
        db_object = self.db.query(ObjectDB).filter(ObjectDB.id == object_id).first()
        
        if not db_object:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {object_id} not found"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 空文字列やNoneのフィールドを除外
        valid_update_dict = {}
        for key, value in update_dict.items():
            if key in ['name', 'summary', 'description']:
                # 文字列フィールドの場合は空文字列や空白のみの場合は除外
                if value is not None and len(str(value).strip()) > 0:
                    self._validate_string_field(key.capitalize(), value)
                    valid_update_dict[key] = value
            elif key == 'photos':
                # photosフィールドの場合（空文字列も許可）
                if value is not None:
                    if value.strip():  # 空文字列でない場合のみJSON形式チェック
                        self._validate_photos_field(value)
                    valid_update_dict[key] = value
        
        # 更新するフィールドがない場合は400エラー
        if not valid_update_dict:
            raise HTTPException(
                status_code=400,
                detail="No valid fields to update. All provided fields are empty or invalid."
            )
        
        for key, value in valid_update_dict.items():
            setattr(db_object, key, value)
        
        self.db.commit()
        
        return Object(
            id=db_object.id,
            name=db_object.name,
            summary=db_object.summary,
            description=db_object.description,
            photos=db_object.photos
        )

    # レコードの削除
    def delete_object(self, object_id: int) -> None:
        db_object = self.db.query(ObjectDB).filter(ObjectDB.id == object_id).first()
        
        if not db_object:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {object_id} not found"
            )
        
        self.db.delete(db_object)
        self.db.commit()

    # オブジェクトに関連するメモリを取得
    def get_object_memories(self, object_id: int, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """オブジェクトに関連するメモリを取得"""
        
        db_query = self.db.query(MemoryDB).filter(MemoryDB.object_id == object_id)
        db_query = db_query.order_by(MemoryDB.importance.desc(), MemoryDB.last_accessed.desc())
        
        if limit:
            db_query = db_query.limit(limit)
        
        memories = db_query.all()
        
        # メモリにアクセスしたのでlast_accessedを更新
        if memories:
            jst = pytz.timezone('Asia/Tokyo')
            current_time = datetime.now(jst)
            for memory in memories:
                memory.last_accessed = current_time
            self.db.commit()
        
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
    def get_object_details(self, object_id: int, memory_limit: Optional[int] = 10, summary_limit: Optional[int] = 10) -> Dict[str, Any]:
        """オブジェクトの詳細情報を取得（メモリとサマリーを含む）"""
        obj = self.get_object(object_id)  # get_objectでHTTPExceptionが発生する可能性がある
        
        object_dict = obj.model_dump()
        object_dict["memories"] = self.get_object_memories(object_id, memory_limit)
        object_dict["summaries"] = self.get_object_summaries(object_id, summary_limit)
        
        return object_dict

# サービスのファクトリー関数
def get_object_service(db: Session) -> ObjectService:
    return ObjectService(db) 