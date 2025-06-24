from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import Summary, SummaryCreate, SummaryUpdate, SummaryQuery
from .service import summary_service

router = APIRouter(prefix="/summaries", tags=["summaries"])

# レコードの作成
@router.post("/", response_model=Summary)
async def create_summary(summary_data: SummaryCreate):
    return summary_service.create_summary(summary_data)

# 単一レコードの取得
@router.get("/{summary_id}", response_model=Summary)
async def get_summary(summary_id: int):
    summary = summary_service.get_summary(summary_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

# レコードの取得（複数）
@router.get("/", response_model=List[Summary])
async def get_summaries(
    object_id: int = Query(..., description="オブジェクトID"),
    limit: Optional[int] = Query(10, description="取得件数制限")
):
    query = SummaryQuery(
        object_id=object_id,
        limit=limit
    )
    return summary_service.get_summaries(query)

# レコードの更新
@router.put("/{summary_id}", response_model=Summary)
async def update_summary(summary_id: int, update_data: SummaryUpdate):
    summary = summary_service.update_summary(summary_id, update_data)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

# レコードの削除
@router.delete("/{summary_id}")
async def delete_summary(summary_id: int):
    success = summary_service.delete_summary(summary_id)
    if not success:
        raise HTTPException(status_code=404, detail="Summary not found")
    return {"message": f"Summary {summary_id} deleted successfully"} 