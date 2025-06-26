from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Summary, SummaryCreate, SummaryUpdate, SummaryQuery

class SummaryService:
    def __init__(self):
        # インメモリデータストレージ（実際のプロジェクトではデータベースを使用）
        self.summaries: List[Dict[str, Any]] = []
        self.summary_id_counter = 1

    # レコードの作成
    def create_summary(self, summary_data: SummaryCreate) -> Summary:
        summary_dict = summary_data.dict()
        summary_dict["id"] = self.summary_id_counter
        summary_dict["created_at"] = datetime.now()
        
        self.summary_id_counter += 1
        self.summaries.append(summary_dict)
        
        return Summary(**summary_dict)

    # 単一レコードの取得
    def get_summary(self, summary_id: int) -> Optional[Summary]:
        for summary in self.summaries:
            if summary["id"] == summary_id:
                return Summary(**summary)
        return None

    # レコードの取得（複数）
    def get_summaries(self, query: SummaryQuery) -> List[Summary]:
        filtered_summaries = []
        
        for summary in self.summaries:
            if summary["object_id"] != query.object_id:
                continue
                
            filtered_summaries.append(Summary(**summary))
        
        # 作成日時でソート（新しい順）
        filtered_summaries.sort(
            key=lambda x: x.created_at, 
            reverse=True
        )
        
        if query.limit:
            filtered_summaries = filtered_summaries[:query.limit]
            
        return filtered_summaries

    # レコードの更新
    def update_summary(self, summary_id: int, update_data: SummaryUpdate) -> Optional[Summary]:
        for i, summary in enumerate(self.summaries):
            if summary["id"] == summary_id:
                update_dict = update_data.dict(exclude_unset=True)
                summary.update(update_dict)
                return Summary(**summary)
        return None

    # レコードの削除
    def delete_summary(self, summary_id: int) -> bool:
        for i, summary in enumerate(self.summaries):
            if summary["id"] == summary_id:
                self.summaries.pop(i)
                return True
        return False

# グローバルインスタンス
summary_service = SummaryService() 