from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Summary, SummaryCreate, SummaryUpdate, SummaryQuery
from .service import get_summary_service
from utils.database import get_db

router = APIRouter(prefix="/summaries", tags=["summaries"])

# レコードの作成
@router.post("/", response_model=Summary)
async def create_summary(summary_data: SummaryCreate, db: Session = Depends(get_db)):
    summary_service = get_summary_service(db)
    return summary_service.create_summary(summary_data)

# 単一レコードの取得
@router.get("/{summary_id}", response_model=Summary)
async def get_summary(summary_id: int, db: Session = Depends(get_db)):
    summary_service = get_summary_service(db)
    return summary_service.get_summary(summary_id)

# レコードの取得（複数）
@router.get("/", response_model=List[Summary])
async def get_summaries(
    object_id: int = Query(..., description="オブジェクトID"),
    limit: Optional[int] = Query(10, description="取得件数制限"),
    db: Session = Depends(get_db)
):
    summary_service = get_summary_service(db)
    query = SummaryQuery(
        object_id=object_id,
        limit=limit
    )
    return summary_service.get_summaries(query)

# レコードの更新
@router.put("/{summary_id}", response_model=Summary)
async def update_summary(summary_id: int, update_data: SummaryUpdate, db: Session = Depends(get_db)):
    summary_service = get_summary_service(db)
    return summary_service.update_summary(summary_id, update_data)

# レコードの削除
@router.delete("/{summary_id}")
async def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    summary_service = get_summary_service(db)
    summary_service.delete_summary(summary_id)
    return {"message": f"Summary {summary_id} deleted successfully"} 