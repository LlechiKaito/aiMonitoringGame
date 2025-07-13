import pytest
from fastapi import HTTPException
from objects.service import ObjectService
from objects.models import ObjectCreate, ObjectUpdate, ObjectQuery
from utils.db_models import ObjectDB, MemoryDB, SummaryDB
import pytz


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

    def test_create_object_empty_name(self, db_session):
        """nameが空文字列の場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="",  # 空文字列
            summary="テストサマリー",
            description="テスト説明"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_object(object_data)
        
        assert exc_info.value.status_code == 400
        assert "Name must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_object_empty_summary(self, db_session):
        """summaryが空文字列の場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="",  # 空文字列
            description="テスト説明"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_object(object_data)
        
        assert exc_info.value.status_code == 400
        assert "Summary must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_object_empty_description(self, db_session):
        """descriptionが空文字列の場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description=""  # 空文字列
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_object(object_data)
        
        assert exc_info.value.status_code == 400
        assert "Description must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_object_whitespace_only_name(self, db_session):
        """nameが空白のみの場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="   ",  # 空白のみ
            summary="テストサマリー",
            description="テスト説明"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_object(object_data)
        
        assert exc_info.value.status_code == 400
        assert "Name must be at least 1 character long" in str(exc_info.value.detail)



    def test_create_object_empty_photos(self, db_session):
        """photosが空文字列の場合も正常に作成できることを確認"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description="テスト説明",
            photos=""  # 空文字列
        )
        
        result = service.create_object(object_data)
        
        assert result.name == "テストオブジェクト"
        assert result.summary == "テストサマリー"
        assert result.description == "テスト説明"
        assert result.photos == ""

    def test_create_object_whitespace_only_photos(self, db_session):
        """photosが空白のみの場合も正常に作成できることを確認"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description="テスト説明",
            photos="   "  # 空白のみ
        )
        
        result = service.create_object(object_data)
        
        assert result.name == "テストオブジェクト"
        assert result.summary == "テストサマリー"
        assert result.description == "テスト説明"
        assert result.photos == "   "

    def test_create_object_invalid_json_photos(self, db_session):
        """photosが無効なJSON形式の場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description="テスト説明",
            photos="{invalid json}"  # 無効なJSON
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_object(object_data)
        
        assert exc_info.value.status_code == 400
        assert "Photos must be valid JSON format" in str(exc_info.value.detail)

    def test_create_object_valid_json_photos(self, db_session):
        """photosが有効なJSON形式の場合の正常テスト"""
        service = ObjectService(db_session)
        
        object_data = ObjectCreate(
            name="テストオブジェクト",
            summary="テストサマリー",
            description="テスト説明",
            photos='["photo1.jpg", "photo2.jpg"]'  # 有効なJSON
        )
        
        result = service.create_object(object_data)
        
        assert result.name == "テストオブジェクト"
        assert result.summary == "テストサマリー"
        assert result.description == "テスト説明"
        assert result.photos == '["photo1.jpg", "photo2.jpg"]'
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
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_object(999)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)
    
    def test_get_objects_empty_name_validation(self, db_session):
        """空のnameでバリデーションエラーテスト"""
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
        
        query = ObjectQuery(name="", limit=10)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_objects(query)
        
        assert exc_info.value.status_code == 400
        assert "Search name must be at least 1 character long" in str(exc_info.value.detail)
    
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

    def test_get_objects_sorting_by_id_desc(self, db_session):
        """オブジェクト取得がID降順でソートされることを確認"""
        service = ObjectService(db_session)
        
        # 複数のオブジェクトを作成（時系列順）
        created_objects = []
        for i in range(3):
            object_data = ObjectCreate(
                name=f"ソートテストオブジェクト{i}",
                summary=f"サマリー{i}",
                description=f"説明{i}"
            )
            created_obj = service.create_object(object_data)
            created_objects.append(created_obj)
        
        # 名前でフィルタして取得
        query = ObjectQuery(name="ソートテスト", limit=10)
        result = service.get_objects(query)
        
        # ID降順でソートされていることを確認
        assert len(result) == 3
        assert result[0].id > result[1].id > result[2].id
        
        # 最新作成（最大ID）が最初に来ることを確認
        assert result[0].id == created_objects[2].id  # 最後に作成されたもの
        assert result[1].id == created_objects[1].id  # 2番目に作成されたもの
        assert result[2].id == created_objects[0].id  # 最初に作成されたもの

    def test_get_objects_limit(self, db_session):
        """オブジェクト取得の制限テスト"""
        service = ObjectService(db_session)
        
        # テスト用のオブジェクトを複数作成
        for i in range(5):
            object_data = ObjectCreate(
                name=f"テストオブジェクト{i}",
                summary=f"テストサマリー{i}",
                description=f"テスト説明{i}"
            )
            service.create_object(object_data)
        
        # 制限を設けて取得
        query = ObjectQuery(name="オブジェクト", limit=3)
        result = service.get_objects(query)
        
        assert len(result) == 3

    def test_get_objects_empty_name_validation_2(self, db_session):
        """空のnameでバリデーションエラーテスト（その2）"""
        service = ObjectService(db_session)
        
        # オブジェクトが存在しない状態でクエリ
        query = ObjectQuery(name="", limit=10)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_objects(query)
        
        assert exc_info.value.status_code == 400
        assert "Search name must be at least 1 character long" in str(exc_info.value.detail)

    def test_get_objects_none_name_validation(self, db_session):
        """nameがNoneの場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        query = ObjectQuery(limit=10)  # nameがNone
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_objects(query)
        
        assert exc_info.value.status_code == 400
        assert "Search name must be at least 1 character long" in str(exc_info.value.detail)

    def test_get_objects_by_name_not_found(self, db_session, sample_object):
        """名前で検索して該当するオブジェクトが存在しない場合の404エラーテスト"""
        service = ObjectService(db_session)
        
        # 存在しない名前で検索
        query = ObjectQuery(name="存在しないオブジェクト", limit=10)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_objects(query)
        
        assert exc_info.value.status_code == 404
        assert "No objects found with name containing '存在しないオブジェクト'" in str(exc_info.value.detail)

    def test_get_objects_empty_search_name(self, db_session):
        """検索時にnameが空文字列の場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        query = ObjectQuery(name="", limit=10)  # 空文字列
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_objects(query)
        
        assert exc_info.value.status_code == 400
        assert "Search name must be at least 1 character long" in str(exc_info.value.detail)

    def test_get_objects_whitespace_only_search_name(self, db_session):
        """検索時にnameが空白のみの場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        query = ObjectQuery(name="   ", limit=10)  # 空白のみ
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_objects(query)
        
        assert exc_info.value.status_code == 400
        assert "Search name must be at least 1 character long" in str(exc_info.value.detail)
    
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
        """存在しないオブジェクトの更新時の404エラーテスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            name="更新されたオブジェクト",
            summary="更新されたサマリー",
            description="更新された説明"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_object(999, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)

    def test_update_object_invalid_json_photos(self, db_session, sample_object):
        """更新時にphotosが無効なJSON形式の場合のバリデーションエラーテスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            photos="{invalid json}"  # 無効なJSON
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_object(sample_object.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "Photos must be valid JSON format" in str(exc_info.value.detail)

    def test_update_object_valid_json_photos(self, db_session, sample_object):
        """更新時にphotosが有効なJSON形式の場合の正常テスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            photos='["updated_photo1.jpg", "updated_photo2.jpg"]'  # 有効なJSON
        )
        
        result = service.update_object(sample_object.id, update_data)
        
        assert result.photos == '["updated_photo1.jpg", "updated_photo2.jpg"]'
        assert result.id == sample_object.id

    def test_update_object_empty_photos(self, db_session, sample_object):
        """更新時にphotosが空文字列の場合も正常に更新できることを確認"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(photos="")
        result = service.update_object(sample_object.id, update_data)
        
        assert result.photos == ""

    def test_update_object_whitespace_only_photos(self, db_session, sample_object):
        """更新時にphotosが空白のみの場合も正常に更新できることを確認"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(photos="   ")
        result = service.update_object(sample_object.id, update_data)
        
        assert result.photos == "   "

    def test_update_object_skip_empty_fields(self, db_session, sample_object):
        """更新時に空フィールドをスキップして有効フィールドのみ更新するテスト"""
        service = ObjectService(db_session)
        
        original_name = sample_object.name
        original_summary = sample_object.summary
        
        # descriptionのみ更新、nameとsummaryは空文字列でスキップされる
        update_data = ObjectUpdate(
            name="",  # 空文字列（スキップされる）
            summary="   ",  # 空白のみ（スキップされる）
            description="更新された説明"  # 有効な値
        )
        
        result = service.update_object(sample_object.id, update_data)
        
        # nameとsummaryは変更されず、descriptionのみ更新される
        assert result.name == original_name
        assert result.summary == original_summary
        assert result.description == "更新された説明"
        assert result.id == sample_object.id

    def test_update_object_skip_none_fields(self, db_session, sample_object):
        """更新時にNoneフィールドをスキップして有効フィールドのみ更新するテスト"""
        service = ObjectService(db_session)
        
        original_description = sample_object.description
        original_photos = sample_object.photos
        
        # nameとsummaryのみ更新、descriptionとphotosはNoneでスキップされる
        update_data = ObjectUpdate(
            name="更新されたオブジェクト",
            summary="更新されたサマリー",
            description=None,  # None（スキップされる）
            photos=None  # None（スキップされる）
        )
        
        result = service.update_object(sample_object.id, update_data)
        
        # descriptionとphotosは変更されず、nameとsummaryのみ更新される
        assert result.name == "更新されたオブジェクト"
        assert result.summary == "更新されたサマリー"
        assert result.description == original_description
        assert result.photos == original_photos
        assert result.id == sample_object.id

    def test_update_object_all_empty_fields(self, db_session, sample_object):
        """更新時に全フィールドが空の場合の400エラーテスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            name="",  # 空文字列
            summary="   ",  # 空白のみ
            description="",  # 空文字列
            photos=None  # None
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_object(sample_object.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No valid fields to update. All provided fields are empty or invalid." in str(exc_info.value.detail)

    def test_update_object_all_none_fields(self, db_session, sample_object):
        """更新時に全フィールドがNoneの場合の400エラーテスト"""
        service = ObjectService(db_session)
        
        update_data = ObjectUpdate(
            name=None,
            summary=None,
            description=None,
            photos=None
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_object(sample_object.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No valid fields to update. All provided fields are empty or invalid." in str(exc_info.value.detail)

    def test_delete_object_success(self, db_session, sample_object):
        """正常なオブジェクト削除テスト"""
        service = ObjectService(db_session)
        
        # 削除実行（例外が発生しないことを確認）
        service.delete_object(sample_object.id)
        
        # 削除されたか確認（404エラーが発生することを期待）
        with pytest.raises(HTTPException) as exc_info:
            service.get_object(sample_object.id)
        assert exc_info.value.status_code == 404
    
    def test_delete_object_not_found(self, db_session):
        """存在しないオブジェクト削除テスト"""
        service = ObjectService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_object(999)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)
    
    def test_get_object_memories(self, db_session, sample_object):
        """オブジェクトに関連するメモリ取得テスト"""
        service = ObjectService(db_session)
        
        # 関連するメモリを作成
        from datetime import datetime
        memory1 = MemoryDB(
            object_id=sample_object.id,
            content="メモリ1",
            importance=9,
            timestamp=datetime.now(pytz.timezone('Asia/Tokyo')),
            last_accessed=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        memory2 = MemoryDB(
            object_id=sample_object.id,
            content="メモリ2",
            importance=7,
            timestamp=datetime.now(pytz.timezone('Asia/Tokyo')),
            last_accessed=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        
        db_session.add_all([memory1, memory2])
        db_session.commit()
        
        result = service.get_object_memories(sample_object.id, limit=10)
        
        assert len(result) == 2
        # 重要度順でソートされているか確認
        assert result[0]["importance"] >= result[1]["importance"]
        assert all(memory["object_id"] == sample_object.id for memory in result)
    
    def test_get_object_memories_last_accessed_update(self, db_session, sample_object):
        """オブジェクトに関連するメモリ取得時のlast_accessed更新テスト"""
        service = ObjectService(db_session)
        
        # 関連するメモリを作成
        from datetime import datetime
        import time
        jst = pytz.timezone('Asia/Tokyo')
        old_time = datetime.now(jst)
        memory1 = MemoryDB(
            object_id=sample_object.id,
            content="メモリ1",
            importance=9,
            timestamp=old_time,
            last_accessed=old_time
        )
        memory2 = MemoryDB(
            object_id=sample_object.id,
            content="メモリ2",
            importance=7,
            timestamp=old_time,
            last_accessed=old_time
        )
        
        db_session.add_all([memory1, memory2])
        db_session.commit()
        
        # 元のlast_accessedを保存
        original_time1 = memory1.last_accessed
        original_time2 = memory2.last_accessed
        
        # 少し時間を待つ
        time.sleep(0.1)
        
        # メモリを取得
        result = service.get_object_memories(sample_object.id, limit=10)
        
        # メモリがデータベースから再取得してlast_accessedが更新されているか確認
        db_session.refresh(memory1)
        db_session.refresh(memory2)
        
        # last_accessedが更新されているかを確認（時間帯情報を無視して比較）
        assert memory1.last_accessed.replace(tzinfo=None) > original_time1.replace(tzinfo=None)
        assert memory2.last_accessed.replace(tzinfo=None) > original_time2.replace(tzinfo=None)
        assert len(result) == 2
    
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
            created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        summary2 = SummaryDB(
            object_id=sample_object.id,
            key_features="特徴2",
            current_daily_tasks="タスク2",
            recent_progress_feelings="感情2",
            created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
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
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_object_details(999)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail) 