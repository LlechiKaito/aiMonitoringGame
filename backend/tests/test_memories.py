import pytest
from fastapi import HTTPException
from memories.service import MemoryService
from memories.models import MemoryCreate, MemoryUpdate, MemoryQuery
from utils.db_models import ObjectDB, MemoryDB


class TestMemoryService:
    """メモリサービスのテストクラス"""
    
    def test_create_memory_success(self, db_session, sample_object):
        """正常なメモリ作成テスト"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=sample_object.id,
            content="テスト用メモリ",
            importance=0.8
        )
        
        result = service.create_memory(memory_data)
        
        assert result.object_id == sample_object.id
        assert result.content == "テスト用メモリ"
        assert result.importance == 0.8
        assert result.id is not None
        assert result.timestamp is not None
        assert result.last_accessed is not None
    
    def test_create_memory_foreign_key_validation(self, db_session):
        """外部キーバリデーションテスト - 存在しないオブジェクトID"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=999,  # 存在しないID
            content="テスト用メモリ",
            importance=0.8
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_memory(memory_data)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)
    
    def test_get_memory_success(self, db_session, sample_memory):
        """正常なメモリ取得テスト"""
        service = MemoryService(db_session)
        
        result = service.get_memory(sample_memory.id)
        
        assert result is not None
        assert result.id == sample_memory.id
        assert result.content == sample_memory.content
        assert result.importance == sample_memory.importance
        assert result.object_id == sample_memory.object_id
    
    def test_get_memory_not_found(self, db_session):
        """存在しないメモリ取得テスト"""
        service = MemoryService(db_session)
        
        result = service.get_memory(999)
        
        assert result is None
    
    def test_get_memories_by_object_id(self, db_session, sample_object):
        """オブジェクトIDでメモリ一覧取得テスト"""
        service = MemoryService(db_session)
        
        # 複数のメモリを作成
        memory1 = MemoryCreate(
            object_id=sample_object.id,
            content="メモリ1",
            importance=0.9
        )
        memory2 = MemoryCreate(
            object_id=sample_object.id,
            content="メモリ2",
            importance=0.7
        )
        
        service.create_memory(memory1)
        service.create_memory(memory2)
        
        query = MemoryQuery(object_id=sample_object.id, limit=10)
        result = service.get_memories(query)
        
        assert len(result) == 2
        # 重要度順でソートされているか確認
        assert result[0].importance >= result[1].importance
        assert all(memory.object_id == sample_object.id for memory in result)
    
    def test_update_memory_success(self, db_session, sample_memory):
        """正常なメモリ更新テスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            content="更新されたメモリ",
            importance=0.95
        )
        
        result = service.update_memory(sample_memory.id, update_data)
        
        assert result is not None
        assert result.id == sample_memory.id
        assert result.content == "更新されたメモリ"
        assert result.importance == 0.95
    
    def test_update_memory_not_found(self, db_session):
        """存在しないメモリ更新テスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(content="更新されたメモリ")
        result = service.update_memory(999, update_data)
        
        assert result is None
    
    def test_delete_memory_success(self, db_session, sample_memory):
        """正常なメモリ削除テスト"""
        service = MemoryService(db_session)
        
        result = service.delete_memory(sample_memory.id)
        
        assert result is True
        
        # 削除されたか確認
        deleted_memory = service.get_memory(sample_memory.id)
        assert deleted_memory is None
    
    def test_delete_memory_not_found(self, db_session):
        """存在しないメモリ削除テスト"""
        service = MemoryService(db_session)
        
        result = service.delete_memory(999)
        
        assert result is False
    
    def test_memory_query_limit(self, db_session, sample_object):
        """メモリクエリのリミット機能テスト"""
        service = MemoryService(db_session)
        
        # 5つのメモリを作成
        for i in range(5):
            memory_data = MemoryCreate(
                object_id=sample_object.id,
                content=f"メモリ{i}",
                importance=0.5 + i * 0.1
            )
            service.create_memory(memory_data)
        
        # リミット3で取得
        query = MemoryQuery(object_id=sample_object.id, limit=3)
        result = service.get_memories(query)
        
        assert len(result) == 3
        # 重要度順でソートされているか確認
        for i in range(len(result) - 1):
            assert result[i].importance >= result[i + 1].importance
    
    def test_memory_last_accessed_update(self, db_session, sample_memory):
        """メモリアクセス時のlast_accessed更新テスト"""
        service = MemoryService(db_session)
        
        original_last_accessed = sample_memory.last_accessed
        
        # 少し待ってからアクセス
        import time
        time.sleep(0.1)
        
        result = service.get_memory(sample_memory.id)
        
        assert result is not None
        assert result.last_accessed > original_last_accessed 