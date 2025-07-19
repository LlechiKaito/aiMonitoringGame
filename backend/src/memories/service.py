from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Memory, MemoryCreate, MemoryUpdate, MemoryQuery
from utils.db_models import MemoryDB, ObjectDB
from utils.database import get_db
import pytz

class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_importance(self, importance: int) -> None:
        """importanceの値が1から9の範囲内であることを確認"""
        if importance < 1 or importance > 9:
            raise HTTPException(
                status_code=400,
                detail="Importance must be between 1 and 9"
            )

    def _validate_content(self, content: str) -> None:
        """contentが1文字以上であることを確認"""
        if not content or len(content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Content must be at least 1 character long"
            )

    # レコードの作成
    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        # contentのバリデーション
        self._validate_content(memory_data.content)
        
        # importanceのバリデーション
        self._validate_importance(memory_data.importance)
        
        # 外部キー（object_id）の存在確認
        existing_object = self.db.query(ObjectDB).filter(ObjectDB.id == memory_data.object_id).first()
        if not existing_object:
            raise HTTPException(
                status_code=404,
                detail=f"Object with id {memory_data.object_id} not found"
            )
        
        db_memory = MemoryDB(
            object_id=memory_data.object_id,
            content=memory_data.content,
            importance=memory_data.importance,
            timestamp=datetime.now(pytz.timezone('Asia/Tokyo')),
            last_accessed=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        
        self.db.add(db_memory)
        self.db.commit()
        self.db.refresh(db_memory)
        
        return Memory(
            id=db_memory.id,
            object_id=db_memory.object_id,
            content=db_memory.content,
            importance=db_memory.importance,
            timestamp=db_memory.timestamp,
            last_accessed=db_memory.last_accessed
        )

    # 単一レコードの取得
    def get_memory(self, memory_id: int) -> Memory:
        db_memory = self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
        
        if not db_memory:
            raise HTTPException(
                status_code=404,
                detail=f"Memory with id {memory_id} not found"
            )
        
        # last_accessedを更新
        db_memory.last_accessed = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.db.commit()
        
        return Memory(
            id=db_memory.id,
            object_id=db_memory.object_id,
            content=db_memory.content,
            importance=db_memory.importance,
            timestamp=db_memory.timestamp,
            last_accessed=db_memory.last_accessed
        )

    # レコードの取得（複数）
    def get_memories(self, query: MemoryQuery) -> List[Memory]:
        db_query = self.db.query(MemoryDB).filter(MemoryDB.object_id == query.object_id)
        
        # 重要度と最後のアクセス時間でソート
        db_query = db_query.order_by(MemoryDB.importance.desc(), MemoryDB.last_accessed.desc())
        
        if query.limit:
            db_query = db_query.limit(query.limit)
        
        db_memories = db_query.all()
        
        # 結果が空の場合は404エラーを発生
        if not db_memories:
            raise HTTPException(
                status_code=404,
                detail=f"No memories found for object_id {query.object_id}"
            )
        
        # 取得したすべてのmemoryのlast_accessedを更新
        current_time = datetime.now(pytz.timezone('Asia/Tokyo'))
        for db_memory in db_memories:
            db_memory.last_accessed = current_time
        
        self.db.commit()
        
        return [
            Memory(
                id=db_memory.id,
                object_id=db_memory.object_id,
                content=db_memory.content,
                importance=db_memory.importance,
                timestamp=db_memory.timestamp,
                last_accessed=db_memory.last_accessed
            )
            for db_memory in db_memories
        ]

    # レコードの更新
    def update_memory(self, memory_id: int, update_data: MemoryUpdate) -> Memory:
        db_memory = self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
        
        if not db_memory:
            raise HTTPException(
                status_code=404,
                detail=f"Memory with id {memory_id} not found"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 空文字列やNoneのフィールドを除外
        valid_update_dict = {}
        for key, value in update_dict.items():
            if key == 'content':
                # contentの場合は空文字列や空白のみの場合は除外
                if value is not None and len(str(value).strip()) > 0:
                    self._validate_content(value)
                    valid_update_dict[key] = value
            elif key == 'importance':
                # importanceの場合はNoneでなければバリデーション
                if value is not None:
                    self._validate_importance(value)
                    valid_update_dict[key] = value
        
        # 更新するフィールドがない場合は400エラー
        if not valid_update_dict:
            raise HTTPException(
                status_code=400,
                detail="No valid fields to update. All provided fields are empty or invalid."
            )
        
        for key, value in valid_update_dict.items():
            setattr(db_memory, key, value)
        
        db_memory.last_accessed = datetime.now(pytz.timezone('Asia/Tokyo'))
        self.db.commit()
        
        return Memory(
            id=db_memory.id,
            object_id=db_memory.object_id,
            content=db_memory.content,
            importance=db_memory.importance,
            timestamp=db_memory.timestamp,
            last_accessed=db_memory.last_accessed
        )

    # レコードの削除
    def delete_memory(self, memory_id: int) -> None:
        db_memory = self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
        
        if not db_memory:
            raise HTTPException(
                status_code=404,
                detail=f"Memory with id {memory_id} not found"
            )
        
        self.db.delete(db_memory)
        self.db.commit()

# サービスのファクトリー関数
def get_memory_service(db: Session) -> MemoryService:
    return MemoryService(db) 