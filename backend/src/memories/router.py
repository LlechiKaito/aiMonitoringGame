from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import Memory, MemoryCreate, MemoryUpdate, MemoryQuery
from .service import memory_service

router = APIRouter(prefix="/memories", tags=["memories"])

# レコードの作成
@router.post("/", response_model=Memory)
async def create_memory(memory_data: MemoryCreate):
    return memory_service.create_memory(memory_data)

# 単一レコードの取得
@router.get("/{memory_id}", response_model=Memory)
async def get_memory(memory_id: int):
    memory = memory_service.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

# レコードの取得（複数）
@router.get("/", response_model=List[Memory])
async def get_memories(
    object_id: int = Query(..., description="オブジェクトID"),
    min_importance: Optional[float] = Query(None, description="最小重要度"),
    limit: Optional[int] = Query(10, description="取得件数制限")
):
    query = MemoryQuery(
        object_id=object_id,
        min_importance=min_importance,
        limit=limit
    )
    return memory_service.get_memories(query)

# レコードの更新
@router.put("/{memory_id}", response_model=Memory)
async def update_memory(memory_id: int, update_data: MemoryUpdate):
    memory = memory_service.update_memory(memory_id, update_data)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

# レコードの削除
@router.delete("/{memory_id}")
async def delete_memory(memory_id: int):
    success = memory_service.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": f"Memory {memory_id} deleted successfully"}