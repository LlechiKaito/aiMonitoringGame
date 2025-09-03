from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Memory, MemoryCreate, MemoryUpdate, MemoryQuery
from .service import get_memory_service
from utils.database import get_db

router = APIRouter(prefix="/memories", tags=["memories"])

# レコードの作成
@router.post("/", response_model=Memory)
async def create_memory(memory_data: MemoryCreate, db: Session = Depends(get_db)):
    memory_service = get_memory_service(db)
    return memory_service.create_memory(memory_data)

# 単一レコードの取得
@router.get("/{memory_id}", response_model=Memory)
async def get_memory(memory_id: int, db: Session = Depends(get_db)):
    memory_service = get_memory_service(db)
    return memory_service.get_memory(memory_id)

# レコードの取得（複数）
@router.get("/", response_model=List[Memory])
async def get_memories(
    object_id: Optional[int] = Query(None, description="オブジェクトID"),
    query: Optional[str] = Query(None, description="検索クエリ"),
    limit: Optional[int] = Query(5, description="取得件数制限"),
    db: Session = Depends(get_db)
):
    memory_service = get_memory_service(db)
    query = MemoryQuery(
        object_id=object_id,
        query=query,
        limit=limit
    )
    return memory_service.get_memories(query)

# レコードの更新
@router.put("/{memory_id}", response_model=Memory)
async def update_memory(memory_id: int, update_data: MemoryUpdate, db: Session = Depends(get_db)):
    memory_service = get_memory_service(db)
    return memory_service.update_memory(memory_id, update_data)

# レコードの削除
@router.delete("/{memory_id}")
async def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    memory_service = get_memory_service(db)
    memory_service.delete_memory(memory_id)
    return {"message": f"Memory {memory_id} deleted successfully"}