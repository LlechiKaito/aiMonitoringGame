from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Memory, MemoryCreate, MemoryUpdate, MemoryQuery

class MemoryService:
    def __init__(self):
        # インメモリデータストレージ（実際のプロジェクトではデータベースを使用）
        self.memories: List[Dict[str, Any]] = []
        self.memory_id_counter = 1

    # レコードの作成
    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        memory_dict = memory_data.dict()
        memory_dict["id"] = self.memory_id_counter
        memory_dict["timestamp"] = datetime.now()
        memory_dict["last_accessed"] = datetime.now()
        
        self.memory_id_counter += 1
        self.memories.append(memory_dict)
        
        return Memory(**memory_dict)

    # 単一レコードの取得
    def get_memory(self, memory_id: int) -> Optional[Memory]:
        for memory in self.memories:
            if memory["id"] == memory_id:
                memory["last_accessed"] = datetime.now()
                return Memory(**memory)
        return None

    # レコードの取得（複数）
    def get_memories(self, query: MemoryQuery) -> List[Memory]:
        filtered_memories = []
        
        for memory in self.memories:
            if memory["object_id"] != query.object_id:
                continue
                
            if query.min_importance and memory["importance"] < query.min_importance:
                continue
                
            filtered_memories.append(Memory(**memory))
        
        filtered_memories.sort(
            key=lambda x: (x.importance, x.last_accessed), 
            reverse=True
        )
        
        if query.limit:
            filtered_memories = filtered_memories[:query.limit]
            
        return filtered_memories

    # レコードの更新
    def update_memory(self, memory_id: int, update_data: MemoryUpdate) -> Optional[Memory]:
        for i, memory in enumerate(self.memories):
            if memory["id"] == memory_id:
                update_dict = update_data.dict(exclude_unset=True)
                memory.update(update_dict)
                memory["last_accessed"] = datetime.now()
                return Memory(**memory)
        return None

    # レコードの削除
    def delete_memory(self, memory_id: int) -> bool:
        for i, memory in enumerate(self.memories):
            if memory["id"] == memory_id:
                self.memories.pop(i)
                return True
        return False

# グローバルインスタンス
memory_service = MemoryService() 