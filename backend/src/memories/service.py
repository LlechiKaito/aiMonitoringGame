from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Memory, MemoryCreate, MemoryUpdate, MemoryQuery
from utils.db_models import MemoryDB, ObjectDB
from utils.database import get_db

class MemoryService:
    def __init__(self, db: Session):
        self.db = db

    # レコードの作成
    def create_memory(self, memory_data: MemoryCreate) -> Memory:
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
            timestamp=datetime.now(),
            last_accessed=datetime.now()
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
    def get_memory(self, memory_id: int) -> Optional[Memory]:
        db_memory = self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
        
        if db_memory:
            # last_accessedを更新
            db_memory.last_accessed = datetime.now()
            self.db.commit()
            
            return Memory(
                id=db_memory.id,
                object_id=db_memory.object_id,
                content=db_memory.content,
                importance=db_memory.importance,
                timestamp=db_memory.timestamp,
                last_accessed=db_memory.last_accessed
            )
        return None

    # レコードの取得（複数）
    def get_memories(self, query: MemoryQuery) -> List[Memory]:
        db_query = self.db.query(MemoryDB).filter(MemoryDB.object_id == query.object_id)
        
        # 重要度と最後のアクセス時間でソート
        db_query = db_query.order_by(MemoryDB.importance.desc(), MemoryDB.last_accessed.desc())
        
        if query.limit:
            db_query = db_query.limit(query.limit)
        
        db_memories = db_query.all()
        
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
    def update_memory(self, memory_id: int, update_data: MemoryUpdate) -> Optional[Memory]:
        db_memory = self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
        
        if db_memory:
            update_dict = update_data.dict(exclude_unset=True)
            
            for key, value in update_dict.items():
                setattr(db_memory, key, value)
            
            db_memory.last_accessed = datetime.now()
            self.db.commit()
            
            return Memory(
                id=db_memory.id,
                object_id=db_memory.object_id,
                content=db_memory.content,
                importance=db_memory.importance,
                timestamp=db_memory.timestamp,
                last_accessed=db_memory.last_accessed
            )
        return None

    # レコードの削除
    def delete_memory(self, memory_id: int) -> bool:
        db_memory = self.db.query(MemoryDB).filter(MemoryDB.id == memory_id).first()
        
        if db_memory:
            self.db.delete(db_memory)
            self.db.commit()
            return True
        return False

# サービスのファクトリー関数
def get_memory_service(db: Session) -> MemoryService:
    return MemoryService(db) 