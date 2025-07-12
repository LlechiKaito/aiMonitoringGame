import pytest
from objects.service import ObjectService
from objects.models import ObjectCreate, ObjectUpdate, ObjectQuery
from utils.db_models import ObjectDB, MemoryDB, SummaryDB


class TestObjectService:
    """オブジェクトサービスのテストクラス"""
    
    def test_create_object_success(self, db_session):
        """正常なオブジェクト作成テスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description="テスト用の説明",
            photos='[["photo1.jpg", "photo2.jpg"], ["photo3.jpg"]]'
        )
        
        result = service.create_object(object_data)
        
        assert result.name == "テストオブジェクト"
        assert result.summary == "テストサマリー"
        assert result.description == "テスト用の説明"
        assert result.photos == '[["photo1.jpg", "photo2.jpg"], ["photo3.jpg"]]'
        assert result.id is not None
    
    def test_create_object_with_default_photos(self, db_session):
        """デフォルトの写真配列でオブジェクト作成テスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description="テスト用の説明"
            # photosは省略（デフォルト値を使用）
        )
        
        result = service.create_object(object_data)
        
        assert result.name == "テストオブジェクト"
        assert result.summary == "テストサマリー"
        assert result.description == "テスト用の説明"
        assert result.photos == "[]"
        assert result.id is not None
    
    def test_get_object_success(self, db_session, sample_object):
        """正常なオブジェクト取得テスト"""
        service = ObjectService(db_session)
        
        result = service.get_object(sample_object.id)
        
        assert result is not None
        assert result.id == sample_object.id
        assert result.name == sample_object.name
        assert result.summary == sample_object.summary
        assert result.description == sample_object.description
        assert result.photos == sample_object.photos
    
    def test_get_object_not_found(self, db_session):
        """存在しないオブジェクト取得テスト"""
        service = ObjectService(db_session)
        
        result = service.get_object(999)
        
        assert result is None
    
    def test_get_objects_all(self, db_session):
        """全オブジェクト取得テスト"""
        service = ObjectService(db_session)
        
        # 複数のオブジェクトを作成
        object1 = ObjectCreate(
            name="オブジェクト1",
            summary="サマリー1",
            description="説明1"
        )
        object2 = ObjectCreate(
            name="オブジェクト2",
            summary="サマリー2",
            description="説明2"
        )
        
        service.create_object(object1)
        service.create_object(object2)
        
        query = ObjectQuery(limit=10)
        result = service.get_objects(query)
        
        assert len(result) == 2
        # IDの降順でソートされているか確認
        assert result[0].id > result[1].id
    
    def test_get_objects_by_name_filter(self, db_session):
        """名前フィルタでオブジェクト取得テスト"""
        service = ObjectService(db_session)
        
        # 複数のオブジェクトを作成
        object1 = ObjectCreate(
            name="特別なオブジェクト",
            summary="サマリー1",
            description="説明1"
        )
        object2 = ObjectCreate(
            name="普通のオブジェクト",
            summary="サマリー2",
            description="説明2"
        )
        
        service.create_object(object1)
        service.create_object(object2)
        
        query = ObjectQuery(name="特別", limit=10)
        result = service.get_objects(query)
        
        assert len(result) == 1
        assert "特別" in result[0].name
    
    def test_get_objects_limit(self, db_session):
        """リミット機能テスト"""
        service = ObjectService(db_session)
        
        # 5つのオブジェクトを作成
        for i in range(5):
            object_data = ObjectCreate(
                name=f"オブジェクト{i}",
                summary=f"サマリー{i}",
                description=f"説明{i}"
            )
            service.create_object(object_data)
        
        query = ObjectQuery(limit=3)
        result = service.get_objects(query)
        
        assert len(result) == 3
        # IDの降順でソートされているか確認
        for i in range(len(result) - 1):
            assert result[i].id > result[i + 1].id
    
    def test_update_object_success(self, db_session, sample_object):
        """正常なオブジェクト更新テスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            name="更新されたオブジェクト",
            summary="更新されたサマリー",
            description="更新された説明",
            photos='[["updated1.jpg", "updated2.jpg"]]'
        )
        
        result = service.update_object(sample_object.id, update_data)
        
        assert result is not None
        assert result.id == sample_object.id
        assert result.name == "更新されたオブジェクト"
        assert result.summary == "更新されたサマリー"
        assert result.description == "更新された説明"
        assert result.photos == '[["updated1.jpg", "updated2.jpg"]]'
    
    def test_update_object_partial(self, db_session, sample_object):
        """部分更新テスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            name="部分更新されたオブジェクト"
            # 他のフィールドは更新しない
        )
        
        result = service.update_object(sample_object.id, update_data)
        
        assert result is not None
        assert result.id == sample_object.id
        assert result.name == "部分更新されたオブジェクト"
        # 他のフィールドは変更されない
        assert result.summary == sample_object.summary
        assert result.description == sample_object.description
        assert result.photos == sample_object.photos
    
    def test_update_object_not_found(self, db_session):
        """存在しないオブジェクト更新テスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(name="更新されたオブジェクト")
        result = service.update_object(999, update_data)
        
        assert result is None
    
    def test_delete_object_success(self, db_session, sample_object):
        """正常なオブジェクト削除テスト"""
        service = ObjectService(db_session)
        
        result = service.delete_object(sample_object.id)
        
        assert result is True
        
        # 削除されたか確認
        deleted_object = service.get_object(sample_object.id)
        assert deleted_object is None
    
    def test_delete_object_not_found(self, db_session):
        """存在しないオブジェクト削除テスト"""
        service = ObjectService(db_session)
        
        result = service.delete_object(999)
        
        assert result is False
    
    def test_get_object_memories(self, db_session, sample_object):
        """オブジェクトに関連するメモリ取得テスト"""
        service = ObjectService(db_session)
        
        # 関連するメモリを作成
        from datetime import datetime
        memory1 = MemoryDB(
            object_id=sample_object.id,
            content="メモリ1",
            importance=0.9,
            timestamp=datetime.now(),
            last_accessed=datetime.now()
        )
        memory2 = MemoryDB(
            object_id=sample_object.id,
            content="メモリ2",
            importance=0.7,
            timestamp=datetime.now(),
            last_accessed=datetime.now()
        )
        
        db_session.add_all([memory1, memory2])
        db_session.commit()
        
        result = service.get_object_memories(sample_object.id, limit=10)
        
        assert len(result) == 2
        # 重要度順でソートされているか確認
        assert result[0]["importance"] >= result[1]["importance"]
        assert all(memory["object_id"] == sample_object.id for memory in result)
    
    def test_get_object_summaries(self, db_session, sample_object):
        """オブジェクトに関連するサマリー取得テスト"""
        service = ObjectService(db_session)
        
        # 関連するサマリーを作成
        from datetime import datetime
        summary1 = SummaryDB(
            object_id=sample_object.id,
            key_features="特徴1",
            current_daily_tasks="タスク1",
            recent_progress_feelings="感情1",
            created_at=datetime.now()
        )
        summary2 = SummaryDB(
            object_id=sample_object.id,
            key_features="特徴2",
            current_daily_tasks="タスク2",
            recent_progress_feelings="感情2",
            created_at=datetime.now()
        )
        
        db_session.add_all([summary1, summary2])
        db_session.commit()
        
        result = service.get_object_summaries(sample_object.id, limit=10)
        
        assert len(result) == 2
        # 作成日時順でソートされているか確認
        assert result[0]["created_at"] >= result[1]["created_at"]
        assert all(summary["object_id"] == sample_object.id for summary in result)
    
    def test_get_object_details(self, db_session, sample_object, sample_memory, sample_summary):
        """オブジェクトの詳細情報取得テスト（メモリとサマリーを含む）"""
        service = ObjectService(db_session)
        
        result = service.get_object_details(sample_object.id)
        
        assert result is not None
        assert result["id"] == sample_object.id
        assert result["name"] == sample_object.name
        assert "memories" in result
        assert "summaries" in result
        assert len(result["memories"]) > 0
        assert len(result["summaries"]) > 0
    
    def test_get_object_details_not_found(self, db_session):
        """存在しないオブジェクトの詳細情報取得テスト"""
        service = ObjectService(db_session)
        
        result = service.get_object_details(999)
        
        assert result is None 