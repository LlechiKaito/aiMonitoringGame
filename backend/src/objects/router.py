from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Object, ObjectCreate, ObjectUpdate, ObjectQuery
from .service import get_object_service
from utils.database import get_db

router = APIRouter(prefix="/objects", tags=["objects"])

# レコードの作成
@router.post("/", response_model=Object)
async def create_object(object_data: ObjectCreate, db: Session = Depends(get_db)):
    object_service = get_object_service(db)
    return object_service.create_object(object_data)

# 単一レコードの取得
@router.get("/{object_id}", response_model=Object)
async def get_object(object_id: int, db: Session = Depends(get_db)):
    object_service = get_object_service(db)
    return object_service.get_object(object_id)

# レコードの取得（複数）
@router.get("/", response_model=List[Object])
async def get_objects(
    name: Optional[str] = Query(None, description="オブジェクト名（部分一致）"),
    limit: Optional[int] = Query(10, description="取得件数制限"),
    db: Session = Depends(get_db)
):
    object_service = get_object_service(db)
    query = ObjectQuery(
        name=name,
        limit=limit
    )
    return object_service.get_objects(query)

# レコードの更新
@router.put("/{object_id}", response_model=Object)
async def update_object(object_id: int, update_data: ObjectUpdate, db: Session = Depends(get_db)):
    object_service = get_object_service(db)
    return object_service.update_object(object_id, update_data)

# レコードの削除
@router.delete("/{object_id}")
async def delete_object(object_id: int, db: Session = Depends(get_db)):
    object_service = get_object_service(db)
    object_service.delete_object(object_id)
    return {"message": f"Object {object_id} deleted successfully"}

# オブジェクトに関連するメモリを取得
@router.get("/{object_id}/memories")
async def get_object_memories(
    object_id: int,
    limit: Optional[int] = Query(10, description="取得件数制限"),
    db: Session = Depends(get_db)
):
    """オブジェクトに関連するメモリを取得"""
    object_service = get_object_service(db)
    # オブジェクトの存在確認
    obj = object_service.get_object(object_id)
    
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
    limit: Optional[int] = Query(10, description="取得件数制限"),
    db: Session = Depends(get_db)
):
    """オブジェクトに関連するサマリーを取得"""
    object_service = get_object_service(db)
    # オブジェクトの存在確認
    obj = object_service.get_object(object_id)
    
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
    summary_limit: Optional[int] = Query(10, description="サマリー取得件数制限"),
    db: Session = Depends(get_db)
):
    """オブジェクトの詳細情報を取得（メモリとサマリーを含む）"""
    object_service = get_object_service(db)
    return object_service.get_object_details(object_id, memory_limit, summary_limit) 