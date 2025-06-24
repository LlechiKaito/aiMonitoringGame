from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import Object, ObjectCreate, ObjectUpdate, ObjectQuery
from .service import object_service

router = APIRouter(prefix="/objects", tags=["objects"])

# レコードの作成
@router.post("/", response_model=Object)
async def create_object(object_data: ObjectCreate):
    return object_service.create_object(object_data)

# 単一レコードの取得
@router.get("/{object_id}", response_model=Object)
async def get_object(object_id: int):
    obj = object_service.get_object(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

# レコードの取得（複数）
@router.get("/", response_model=List[Object])
async def get_objects(
    name: Optional[str] = Query(None, description="オブジェクト名（部分一致）"),
    limit: Optional[int] = Query(10, description="取得件数制限")
):
    query = ObjectQuery(
        name=name,
        limit=limit
    )
    return object_service.get_objects(query)

# レコードの更新
@router.put("/{object_id}", response_model=Object)
async def update_object(object_id: int, update_data: ObjectUpdate):
    obj = object_service.update_object(object_id, update_data)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

# レコードの削除
@router.delete("/{object_id}")
async def delete_object(object_id: int):
    success = object_service.delete_object(object_id)
    if not success:
        raise HTTPException(status_code=404, detail="Object not found")
    return {"message": f"Object {object_id} deleted successfully"}

# オブジェクトに関連するメモリを取得
@router.get("/{object_id}/memories")
async def get_object_memories(
    object_id: int,
    limit: Optional[int] = Query(10, description="取得件数制限")
):
    """オブジェクトに関連するメモリを取得"""
    # オブジェクトの存在確認
    obj = object_service.get_object(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    memories = object_service.get_object_memories(object_id, limit)
    return {
        "object_id": object_id,
        "object_name": obj.name,
        "memories": memories,
        "count": len(memories)
    }

# オブジェクトに関連するサマリーを取得
@router.get("/{object_id}/summaries")
async def get_object_summaries(
    object_id: int,
    limit: Optional[int] = Query(10, description="取得件数制限")
):
    """オブジェクトに関連するサマリーを取得"""
    # オブジェクトの存在確認
    obj = object_service.get_object(object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    summaries = object_service.get_object_summaries(object_id, limit)
    return {
        "object_id": object_id,
        "object_name": obj.name,
        "summaries": summaries,
        "count": len(summaries)
    }

# オブジェクトの詳細情報を取得（メモリとサマリーを含む）
@router.get("/{object_id}/details")
async def get_object_details(
    object_id: int,
    memory_limit: Optional[int] = Query(10, description="メモリ取得件数制限"),
    summary_limit: Optional[int] = Query(10, description="サマリー取得件数制限")
):
    """オブジェクトの詳細情報を取得（メモリとサマリーを含む）"""
    details = object_service.get_object_details(object_id, memory_limit, summary_limit)
    if not details:
        raise HTTPException(status_code=404, detail="Object not found")
    
    return details 