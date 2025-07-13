import pytest
from fastapi import HTTPException
from summaries.service import SummaryService
from summaries.models import SummaryCreate, SummaryUpdate, SummaryQuery
from utils.db_models import ObjectDB, SummaryDB


class TestSummaryService:
    """サマリーサービスのテストクラス"""
    
    def test_create_summary_success(self, db_session, sample_object):
        """正常なサマリー作成テスト"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=sample_object.id,
            key_features="テスト特徴",
            current_daily_tasks="テストタスク",
            recent_progress_feelings="テスト感情"
        )
        
        result = service.create_summary(summary_data)
        
        assert result.object_id == sample_object.id
        assert result.key_features == "テスト特徴"
        assert result.current_daily_tasks == "テストタスク"
        assert result.recent_progress_feelings == "テスト感情"
        assert result.id is not None
        assert result.created_at is not None
    
    def test_create_summary_foreign_key_validation(self, db_session):
        """存在しないオブジェクトIDでサマリー作成時の外部キー制約エラーテスト"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=999,  # 存在しないオブジェクトID
            key_features="テスト特徴",
            current_daily_tasks="テストタスク",
            recent_progress_feelings="テスト感情"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_summary(summary_data)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)

    def test_create_summary_empty_key_features(self, db_session, sample_object):
        """key_featuresが空文字列の場合のバリデーションエラーテスト"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=sample_object.id,
            key_features="",  # 空文字列
            current_daily_tasks="テストタスク",
            recent_progress_feelings="テスト感情"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_summary(summary_data)
        
        assert exc_info.value.status_code == 400
        assert "Key features must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_summary_empty_current_daily_tasks(self, db_session, sample_object):
        """current_daily_tasksが空文字列の場合のバリデーションエラーテスト"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=sample_object.id,
            key_features="テスト特徴",
            current_daily_tasks="",  # 空文字列
            recent_progress_feelings="テスト感情"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_summary(summary_data)
        
        assert exc_info.value.status_code == 400
        assert "Current daily tasks must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_summary_empty_recent_progress_feelings(self, db_session, sample_object):
        """recent_progress_feelingsが空文字列の場合のバリデーションエラーテスト"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=sample_object.id,
            key_features="テスト特徴",
            current_daily_tasks="テストタスク",
            recent_progress_feelings=""  # 空文字列
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_summary(summary_data)
        
        assert exc_info.value.status_code == 400
        assert "Recent progress feelings must be at least 1 character long" in str(exc_info.value.detail)

    def test_create_summary_whitespace_only_key_features(self, db_session, sample_object):
        """key_featuresが空白のみの場合のバリデーションエラーテスト"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=sample_object.id,
            key_features="   ",  # 空白のみ
            current_daily_tasks="テストタスク",
            recent_progress_feelings="テスト感情"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_summary(summary_data)
        
        assert exc_info.value.status_code == 400
        assert "Key features must be at least 1 character long" in str(exc_info.value.detail)
    
    def test_get_summary_success(self, db_session, sample_summary):
        """正常なサマリー取得テスト"""
        service = SummaryService(db_session)
        
        result = service.get_summary(sample_summary.id)
        
        assert result is not None
        assert result.id == sample_summary.id
        assert result.key_features == sample_summary.key_features
        assert result.current_daily_tasks == sample_summary.current_daily_tasks
        assert result.recent_progress_feelings == sample_summary.recent_progress_feelings
        assert result.object_id == sample_summary.object_id
    
    def test_get_summary_not_found(self, db_session):
        """存在しないサマリー取得テスト"""
        service = SummaryService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_summary(999)
        
        assert exc_info.value.status_code == 404
        assert "Summary with id 999 not found" in str(exc_info.value.detail)
    
    def test_get_summaries_by_object_id(self, db_session, sample_object):
        """オブジェクトIDでサマリーを取得するテスト"""
        service = SummaryService(db_session)
        
        # テスト用のサマリーを複数作成
        summaries = []
        for i in range(3):
            summary_data = SummaryCreate(
                object_id=sample_object.id,
                key_features=f"特徴{i}",
                current_daily_tasks=f"タスク{i}",
                recent_progress_feelings=f"感情{i}"
            )
            summaries.append(service.create_summary(summary_data))
        
        # 作成したサマリーを取得
        query = SummaryQuery(object_id=sample_object.id, limit=5)
        result = service.get_summaries(query)
        
        # 取得したサマリーが作成したものと一致することを確認
        assert len(result) == 3
        assert all(summary.object_id == sample_object.id for summary in result)
        # 作成日時順でソートされることを確認
        assert result[0].created_at >= result[1].created_at >= result[2].created_at

    def test_get_summaries_sorting_by_created_at_desc(self, db_session, sample_object):
        """サマリー取得がcreated_at降順でソートされることを確認"""
        import time
        service = SummaryService(db_session)
        
        # 時間差を作ってサマリーを作成
        summary1 = service.create_summary(SummaryCreate(
            object_id=sample_object.id,
            key_features="古いサマリーの特徴",
            current_daily_tasks="古いタスク",
            recent_progress_feelings="古い感情"
        ))
        
        time.sleep(0.01)  # 時間差を確実にするため
        
        summary2 = service.create_summary(SummaryCreate(
            object_id=sample_object.id,
            key_features="新しいサマリーの特徴",
            current_daily_tasks="新しいタスク", 
            recent_progress_feelings="新しい感情"
        ))
        
        # サマリーを取得
        query = SummaryQuery(object_id=sample_object.id, limit=5)
        result = service.get_summaries(query)
        
        # created_at降順でソートされていることを確認
        assert len(result) == 2
        assert result[0].created_at > result[1].created_at
        
        # 新しく作成されたサマリーが最初に来ることを確認
        assert result[0].id == summary2.id  # 後で作成されたもの
        assert result[1].id == summary1.id  # 先に作成されたもの
        
        # 内容の確認
        assert result[0].key_features == "新しいサマリーの特徴"
        assert result[1].key_features == "古いサマリーの特徴"

    def test_get_summaries_not_found(self, db_session, sample_object):
        """該当するサマリーが存在しない場合の404エラーテスト"""
        service = SummaryService(db_session)
        
        # サマリーが存在しないオブジェクトIDでクエリ
        query = SummaryQuery(object_id=sample_object.id, limit=5)
        
        with pytest.raises(HTTPException) as exc_info:
            service.get_summaries(query)
        
        assert exc_info.value.status_code == 404
        assert f"No summaries found for object_id {sample_object.id}" in str(exc_info.value.detail)
    
    def test_update_summary_success(self, db_session, sample_summary):
        """正常なサマリー更新テスト"""
        service = SummaryService(db_session)
        
        update_data = SummaryUpdate(
            key_features="更新された特徴",
            current_daily_tasks="更新されたタスク",
            recent_progress_feelings="更新された感情"
        )
        
        result = service.update_summary(sample_summary.id, update_data)
        
        assert result is not None
        assert result.id == sample_summary.id
        assert result.key_features == "更新された特徴"
        assert result.current_daily_tasks == "更新されたタスク"
        assert result.recent_progress_feelings == "更新された感情"
        assert result.object_id == sample_summary.object_id
    
    def test_update_summary_partial(self, db_session, sample_summary):
        """部分更新テスト"""
        service = SummaryService(db_session)
        
        update_data = SummaryUpdate(
            key_features="部分更新された特徴"
            # 他のフィールドは更新しない
        )
        
        result = service.update_summary(sample_summary.id, update_data)
        
        assert result is not None
        assert result.id == sample_summary.id
        assert result.key_features == "部分更新された特徴"
        # 他のフィールドは変更されない
        assert result.current_daily_tasks == sample_summary.current_daily_tasks
        assert result.recent_progress_feelings == sample_summary.recent_progress_feelings
    
    def test_update_summary_not_found(self, db_session):
        """存在しないサマリーの更新時の404エラーテスト"""
        service = SummaryService(db_session)
        
        update_data = SummaryUpdate(
            key_features="更新された特徴",
            current_daily_tasks="更新されたタスク",
            recent_progress_feelings="更新された感情"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_summary(999, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Summary with id 999 not found" in str(exc_info.value.detail)

    def test_update_summary_skip_empty_fields(self, db_session, sample_summary):
        """更新時に空フィールドをスキップして有効フィールドのみ更新するテスト"""
        service = SummaryService(db_session)
        
        original_key_features = sample_summary.key_features
        original_current_daily_tasks = sample_summary.current_daily_tasks
        
        # recent_progress_feelingsのみ更新、他は空文字列でスキップされる
        update_data = SummaryUpdate(
            key_features="",  # 空文字列（スキップされる）
            current_daily_tasks="   ",  # 空白のみ（スキップされる）
            recent_progress_feelings="更新された感情"  # 有効な値
        )
        
        result = service.update_summary(sample_summary.id, update_data)
        
        # key_featuresとcurrent_daily_tasksは変更されず、recent_progress_feelingsのみ更新される
        assert result.key_features == original_key_features
        assert result.current_daily_tasks == original_current_daily_tasks
        assert result.recent_progress_feelings == "更新された感情"
        assert result.id == sample_summary.id

    def test_update_summary_skip_none_fields(self, db_session, sample_summary):
        """更新時にNoneフィールドをスキップして有効フィールドのみ更新するテスト"""
        service = SummaryService(db_session)
        
        original_recent_progress_feelings = sample_summary.recent_progress_feelings
        
        # key_featuresとcurrent_daily_tasksのみ更新、recent_progress_feelingsはNoneでスキップされる
        update_data = SummaryUpdate(
            key_features="更新された特徴",
            current_daily_tasks="更新されたタスク",
            recent_progress_feelings=None  # None（スキップされる）
        )
        
        result = service.update_summary(sample_summary.id, update_data)
        
        # recent_progress_feelingsは変更されず、他の2つは更新される
        assert result.key_features == "更新された特徴"
        assert result.current_daily_tasks == "更新されたタスク"
        assert result.recent_progress_feelings == original_recent_progress_feelings
        assert result.id == sample_summary.id

    def test_update_summary_all_empty_fields(self, db_session, sample_summary):
        """更新時に全フィールドが空の場合の400エラーテスト"""
        service = SummaryService(db_session)
        
        update_data = SummaryUpdate(
            key_features="",  # 空文字列
            current_daily_tasks="   ",  # 空白のみ
            recent_progress_feelings=""  # 空文字列
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_summary(sample_summary.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No valid fields to update. All provided fields are empty or invalid." in str(exc_info.value.detail)

    def test_update_summary_all_none_fields(self, db_session, sample_summary):
        """更新時に全フィールドがNoneの場合の400エラーテスト"""
        service = SummaryService(db_session)
        
        update_data = SummaryUpdate(
            key_features=None,
            current_daily_tasks=None,
            recent_progress_feelings=None
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_summary(sample_summary.id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No valid fields to update. All provided fields are empty or invalid." in str(exc_info.value.detail)
    
    def test_delete_summary_success(self, db_session, sample_summary):
        """正常なサマリー削除テスト"""
        service = SummaryService(db_session)
        
        # 削除実行（例外が発生しないことを確認）
        service.delete_summary(sample_summary.id)
        
        # 削除されたか確認（404エラーが発生することを期待）
        with pytest.raises(HTTPException) as exc_info:
            service.get_summary(sample_summary.id)
        assert exc_info.value.status_code == 404
    
    def test_delete_summary_not_found(self, db_session):
        """存在しないサマリー削除テスト"""
        service = SummaryService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_summary(999)
        
        assert exc_info.value.status_code == 404
        assert "Summary with id 999 not found" in str(exc_info.value.detail)
    
    def test_summary_query_limit(self, db_session, sample_object):
        """リミット機能テスト"""
        service = SummaryService(db_session)
        
        # 3つのサマリーを作成
        for i in range(3):
            summary_data = SummaryCreate(
                object_id=sample_object.id,
                key_features=f"特徴{i}",
                current_daily_tasks=f"タスク{i}",
                recent_progress_feelings=f"感情{i}"
            )
            service.create_summary(summary_data)
        
        query = SummaryQuery(object_id=sample_object.id, limit=2)
        result = service.get_summaries(query)
        
        assert len(result) == 2
        # 作成日時順でソートされているか確認（新しい順）
        for i in range(len(result) - 1):
            assert result[i].created_at >= result[i + 1].created_at 