from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Object, ObjectCreate, ObjectUpdate, ObjectQuery

# 他のモジュールからサービスをインポート
from memories.service import memory_service
from summaries.service import summary_service

class ObjectService:
    def __init__(self):
        # インメモリデータストレージ（実際のプロジェクトではデータベースを使用）
        self.objects: List[Dict[str, Any]] = []
        self.object_id_counter = 1

    # レコードの作成
    def create_object(self, object_data: ObjectCreate) -> Object:
        object_dict = object_data.dict()
        object_dict["id"] = self.object_id_counter
        
        self.object_id_counter += 1
        self.objects.append(object_dict)
        
        return Object(**object_dict)

    # 単一レコードの取得
    def get_object(self, object_id: int) -> Optional[Object]:
        for obj in self.objects:
            if obj["id"] == object_id:
                return Object(**obj)
        return None

    # レコードの取得（複数）
    def get_objects(self, query: ObjectQuery) -> List[Object]:
        filtered_objects = []
        
        for obj in self.objects:
            if query.name and query.name.lower() not in obj["name"].lower():
                continue
                
            filtered_objects.append(Object(**obj))
        
        # IDでソート（新しい順）
        filtered_objects.sort(
            key=lambda x: x.id, 
            reverse=True
        )
        
        if query.limit:
            filtered_objects = filtered_objects[:query.limit]
            
        return filtered_objects

    # レコードの更新
    def update_object(self, object_id: int, update_data: ObjectUpdate) -> Optional[Object]:
        for i, obj in enumerate(self.objects):
            if obj["id"] == object_id:
                update_dict = update_data.dict(exclude_unset=True)
                obj.update(update_dict)
                return Object(**obj)
        return None

    # レコードの削除
    def delete_object(self, object_id: int) -> bool:
        for i, obj in enumerate(self.objects):
            if obj["id"] == object_id:
                self.objects.pop(i)
                return True
        return False

    # オブジェクトに関連するメモリを取得
    def get_object_memories(self, object_id: int, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """オブジェクトに関連するメモリを取得"""
        from memories.models import MemoryQuery
        
        query = MemoryQuery(object_id=object_id, limit=limit)
        memories = memory_service.get_memories(query)
        return [memory.dict() for memory in memories]

    # オブジェクトに関連するサマリーを取得
    def get_object_summaries(self, object_id: int, limit: Optional[int] = 10) -> List[Dict[str, Any]]:
        """オブジェクトに関連するサマリーを取得"""
        from summaries.models import SummaryQuery
        
        query = SummaryQuery(object_id=object_id, limit=limit)
        summaries = summary_service.get_summaries(query)
        return [summary.dict() for summary in summaries]

    # オブジェクトの詳細情報を取得（メモリとサマリーを含む）
    def get_object_details(self, object_id: int, memory_limit: Optional[int] = 10, summary_limit: Optional[int] = 10) -> Optional[Dict[str, Any]]:
        """オブジェクトの詳細情報を取得（メモリとサマリーを含む）"""
        obj = self.get_object(object_id)
        if not obj:
            return None
        
        object_dict = obj.dict()
        object_dict["memories"] = self.get_object_memories(object_id, memory_limit)
        object_dict["summaries"] = self.get_object_summaries(object_id, summary_limit)
        
        return object_dict

# グローバルインスタンス
object_service = ObjectService() 