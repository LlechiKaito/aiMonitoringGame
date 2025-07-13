import pytest
import time
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
            importance=8
        )
        
        result = service.create_memory(memory_data)
        
        assert result.object_id == sample_object.id
        assert result.content == "テスト用メモリ"
        assert result.importance == 8
        assert result.id is not None
        assert result.timestamp is not None
        assert result.last_accessed is not None
    
    def test_create_memory_foreign_key_validation(self, db_session):
        """存在しないオブジェクトIDでメモリ作成時の外部キー制約エラーテスト"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=999,  # 存在しないオブジェクトID
            content="テスト用メモリ",
            importance=5
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_memory(memory_data)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)

    def test_create_memory_invalid_importance_low(self, db_session, sample_object):
        """importanceが1未満の場合のバリデーションエラーテスト"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=sample_object.id,
            content="テスト用メモリ",
            importance=0  # 無効な値
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_memory(memory_data)
        
        assert exc_info.value.status_code == 400
        assert "Importance must be between 1 and 9" in str(exc_info.value.detail)

    def test_create_memory_invalid_importance_high(self, db_session, sample_object):
        """importanceが9を超える場合のバリデーションエラーテスト"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=sample_object.id,
            content="テスト用メモリ",
            importance=10  # 無効な値
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_memory(memory_data)
        
        assert exc_info.value.status_code == 400
        assert "Importance must be between 1 and 9" in str(exc_info.value.detail)

    def test_create_memory_empty_content(self, db_session, sample_object):
        """contentが空文字列の場合のバリデーションエラーテスト"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=sample_object.id,
            content="",  # 空文字列
            importance=5
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_memory(memory_data)
        
        assert exc_info.value.status_code == 400
        assert "Content must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_memory_whitespace_only_content(self, db_session, sample_object):
        """contentが空白のみの場合のバリデーションエラーテスト"""
        service = MemoryService(db_session)
        
        memory_data = MemoryCreate(
            object_id=sample_object.id,
            content="   ",  # 空白のみ
            importance=5
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_memory(memory_data)
        
        assert exc_info.value.status_code == 400
        assert "Content must be at least 1 character long" in str(exc_info.value.detail)
    
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
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_memory(999)
        
        assert exc_info.value.status_code == 404
        assert "Memory with id 999 not found" in str(exc_info.value.detail)
    
    def test_get_memories_by_object_id(self, db_session, sample_object):
        """オブジェクトIDでメモリを取得するテスト"""
        service = MemoryService(db_session)
        
        # テスト用のメモリを複数作成
        memories = []
        for i in range(3):
            memory_data = MemoryCreate(
                object_id=sample_object.id,
                content=f"メモリ{i}",
                importance=i + 1
            )
            memories.append(service.create_memory(memory_data))
        
        # 作成したメモリを取得
        query = MemoryQuery(object_id=sample_object.id, limit=5)
        result = service.get_memories(query)
        
        # 取得したメモリが作成したものと一致することを確認
        assert len(result) == 3
        assert all(memory.object_id == sample_object.id for memory in result)
        # 重要度順でソートされることを確認
        assert result[0].importance >= result[1].importance >= result[2].importance

    def test_get_memories_not_found(self, db_session, sample_object):
        """該当するメモリが存在しない場合の404エラーテスト"""
        service = MemoryService(db_session)
        
        # メモリが存在しないオブジェクトIDでクエリ
        query = MemoryQuery(object_id=sample_object.id, limit=5)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_memories(query)
        
        assert exc_info.value.status_code == 404
        assert f"No memories found for object_id {sample_object.id}" in str(exc_info.value.detail)
    
    def test_update_memory_success(self, db_session, sample_memory):
        """正常なメモリ更新テスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            content="更新されたメモリ",
            importance=9
        )
        
        result = service.update_memory(sample_memory.id, update_data)
        
        assert result is not None
        assert result.id == sample_memory.id
        assert result.content == "更新されたメモリ"
        assert result.importance == 9
    
    def test_update_memory_not_found(self, db_session):
        """存在しないメモリの更新時の404エラーテスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            content="更新されたコンテンツ",
            importance=7
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_memory(999, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Memory with id 999 not found" in str(exc_info.value.detail)

    def test_update_memory_invalid_importance_low(self, db_session, sample_memory):
        """更新時にimportanceが1未満の場合のバリデーションエラーテスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            importance=0  # 無効な値
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_memory(sample_memory.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "Importance must be between 1 and 9" in str(exc_info.value.detail)

    def test_update_memory_invalid_importance_high(self, db_session, sample_memory):
        """更新時にimportanceが9を超える場合のバリデーションエラーテスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            importance=10  # 無効な値
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_memory(sample_memory.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "Importance must be between 1 and 9" in str(exc_info.value.detail)

    def test_update_memory_skip_empty_fields(self, db_session, sample_memory):
        """更新時に空フィールドをスキップして有効フィールドのみ更新するテスト"""
        service = MemoryService(db_session)
        
        original_content = sample_memory.content
        
        # importanceのみ更新、contentは空文字列でスキップされる
        update_data = MemoryUpdate(
            content="",  # 空文字列（スキップされる）
            importance=9  # 有効な値
        )
        
        result = service.update_memory(sample_memory.id, update_data)
        
        # contentは変更されず、importanceのみ更新される
        assert result.content == original_content
        assert result.importance == 9
        assert result.id == sample_memory.id

    def test_update_memory_skip_none_fields(self, db_session, sample_memory):
        """更新時にNoneフィールドをスキップして有効フィールドのみ更新するテスト"""
        service = MemoryService(db_session)
        
        original_importance = sample_memory.importance
        
        # contentのみ更新、importanceはNoneでスキップされる
        update_data = MemoryUpdate(
            content="更新されたコンテンツ",
            importance=None  # None（スキップされる）
        )
        
        result = service.update_memory(sample_memory.id, update_data)
        
        # importanceは変更されず、contentのみ更新される
        assert result.content == "更新されたコンテンツ"
        assert result.importance == original_importance
        assert result.id == sample_memory.id

    def test_update_memory_all_empty_fields(self, db_session, sample_memory):
        """更新時に全フィールドが空の場合の400エラーテスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            content="",  # 空文字列
            importance=None  # None
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_memory(sample_memory.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No valid fields to update. All provided fields are empty or invalid." in str(exc_info.value.detail)

    def test_update_memory_all_whitespace_fields(self, db_session, sample_memory):
        """更新時に全フィールドが空白のみの場合の400エラーテスト"""
        service = MemoryService(db_session)
        
        update_data = MemoryUpdate(
            content="   ",  # 空白のみ
            importance=None  # None
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_memory(sample_memory.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No valid fields to update. All provided fields are empty or invalid." in str(exc_info.value.detail)
    
    def test_delete_memory_success(self, db_session, sample_memory):
        """正常なメモリ削除テスト"""
        service = MemoryService(db_session)
        
        # 削除実行（例外が発生しないことを確認）
        service.delete_memory(sample_memory.id)
        
        # 削除されたか確認（404エラーが発生することを期待）
        with pytest.raises(HTTPException) as exc_info:
            service.get_memory(sample_memory.id)
        assert exc_info.value.status_code == 404
    
    def test_delete_memory_not_found(self, db_session):
        """存在しないメモリ削除テスト"""
        service = MemoryService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_memory(999)
        
        assert exc_info.value.status_code == 404
        assert "Memory with id 999 not found" in str(exc_info.value.detail)
    
    def test_memory_query_limit(self, db_session, sample_object):
        """メモリクエリのリミット機能テスト"""
        service = MemoryService(db_session)
        
        # 5つのメモリを作成
        for i in range(5):
            memory_data = MemoryCreate(
                object_id=sample_object.id,
                content=f"メモリ{i}",
                importance=5 + i
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
        """単一のメモリー取得でlast_accessedが更新されることを確認"""
        service = MemoryService(db_session)
        
        # 元のlast_accessedを取得
        original_last_accessed = sample_memory.last_accessed
        
        # 少し時間を置く
        time.sleep(0.1)
        
        # メモリーを取得
        memory = service.get_memory(sample_memory.id)
        
        # last_accessedが更新されていることを確認
        assert memory.last_accessed > original_last_accessed

    def test_get_memories_last_accessed_update(self, db_session, sample_object):
        """複数のメモリー取得でlast_accessedが更新されることを確認"""
        service = MemoryService(db_session)
        
        # 複数のメモリーを作成
        memory1 = service.create_memory(MemoryCreate(
            object_id=sample_object.id,
            content="Test memory 1",
            importance=5
        ))
        
        memory2 = service.create_memory(MemoryCreate(
            object_id=sample_object.id,
            content="Test memory 2",
            importance=7
        ))
        
        # 元のlast_accessedを保存
        original_last_accessed_1 = memory1.last_accessed
        original_last_accessed_2 = memory2.last_accessed
        
        # 少し時間を置く
        time.sleep(0.1)
        
        # 複数のメモリーを取得
        query = MemoryQuery(object_id=sample_object.id)
        memories = service.get_memories(query)
        
        # 取得したメモリーのlast_accessedが更新されていることを確認
        for memory in memories:
            if memory.id == memory1.id:
                assert memory.last_accessed > original_last_accessed_1
            elif memory.id == memory2.id:
                assert memory.last_accessed > original_last_accessed_2

    def test_get_memories_sorting_comprehensive(self, db_session, sample_object):
        """複数のメモリー取得でimportance降順→last_accessed降順のソートが正しく動作することを確認"""
        service = MemoryService(db_session)
        
        # 異なるimportanceとlast_accessedを持つメモリーを作成
        memory1 = service.create_memory(MemoryCreate(
            object_id=sample_object.id,
            content="Low importance old",
            importance=3
        ))
        
        time.sleep(0.01)  # 時間差を作る
        
        memory2 = service.create_memory(MemoryCreate(
            object_id=sample_object.id,
            content="High importance old", 
            importance=8
        ))
        
        time.sleep(0.01)
        
        memory3 = service.create_memory(MemoryCreate(
            object_id=sample_object.id,
            content="High importance new",
            importance=8
        ))
        
        time.sleep(0.01)
        
        memory4 = service.create_memory(MemoryCreate(
            object_id=sample_object.id,
            content="Low importance new",
            importance=3
        ))
        
        # メモリーを取得
        query = MemoryQuery(object_id=sample_object.id)
        result = service.get_memories(query)
        
        # ソート順を確認
        assert len(result) == 4
        
        # importance降順→last_accessed降順の順序を確認
        # 1. High importance new (importance=8, 最新)
        # 2. High importance old (importance=8, 古い)  
        # 3. Low importance new (importance=3, 最新)
        # 4. Low importance old (importance=3, 古い)
        
        # importance順の確認
        assert result[0].importance == 8  # High importance new
        assert result[1].importance == 8  # High importance old
        assert result[2].importance == 3  # Low importance new
        assert result[3].importance == 3  # Low importance old
        
        # 同じimportance内でのlast_accessed順の確認
        # importance=8のグループ
        assert result[0].last_accessed >= result[1].last_accessed
        # importance=3のグループ  
        assert result[2].last_accessed >= result[3].last_accessed
        
        # content順の確認（作成順とlast_accessed順が一致するため）
        assert result[0].content == "High importance new"
        assert result[1].content == "High importance old"
        assert result[2].content == "Low importance new" 
        assert result[3].content == "Low importance old" 