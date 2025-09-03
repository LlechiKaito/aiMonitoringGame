from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .models import Memory, MemoryCreate, MemoryUpdate, MemoryQuery
from utils.db_models import MemoryDB, ObjectDB
from utils.database import get_db
import pytz

from src.utils.memories_search import MemoriesSearch

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
        # object_idが空の場合は400エラー
        if not query.object_id:
            raise HTTPException(
                status_code=400,
                detail="Object ID is required"
            )
        
        # クエリが空の場合は400エラー
        if not query.query:
            raise HTTPException(
                status_code=400,
                detail="Query is required"
            )
        
        # スペースと空白のみの場合は400エラー
        if query.query.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Query cannot be only spaces or whitespace"
            )
        
        # クエリが200文字以上の場合は400エラー
        if len(query.query) > 200:
            raise HTTPException(
                status_code=400,
                detail="Query must be less than 50 characters"
            )
            
        # 取得件数が1から10の範囲内であることを確認
        if query.limit < 1 or query.limit > 10:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 10"
            )
        
        # データベースからメモリを取得
        db_memories = self.db.query(MemoryDB).filter(MemoryDB.object_id == query.object_id).all()
        
        # データベースオブジェクトを辞書形式に変換
        memories_data = []
        for db_memory in db_memories:
            memories_data.append({
                "id": db_memory.id,
                "object_id": db_memory.object_id,
                "content": db_memory.content,
                "timestamp": db_memory.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "importance": db_memory.importance,
                "last_accessed": db_memory.last_accessed.strftime('%Y-%m-%d %H:%M:%S')
            })

        # メモリが存在しない場合は404エラー
        if not memories_data:
            raise HTTPException(
                status_code=404,
                detail=f"No memories found for object_id {query.object_id}"
            )

        # MemoriesSearchを使用して検索
        memories_search_result = MemoriesSearch(memories_data, top_n=query.limit)
        search_result = memories_search_result.search(query.query)
        
        # 検索結果からMemoryオブジェクトを作成
        result_memories = []
        for memory_data in search_result['memory']:
            # 元のデータベースオブジェクトを取得
            db_memory = next(m for m in db_memories if m.id == memory_data['id'])
            
            result_memories.append(Memory(
                id=db_memory.id,
                object_id=db_memory.object_id,
                content=db_memory.content,
                importance=db_memory.importance,
                timestamp=db_memory.timestamp,
                last_accessed=db_memory.last_accessed
            ))
        
        return result_memories

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