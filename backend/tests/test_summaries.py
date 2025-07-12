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
        """外部キーバリデーションテスト - 存在しないオブジェクトID"""
        service = SummaryService(db_session)
        
        summary_data = SummaryCreate(
            object_id=999,  # 存在しないID
            key_features="テスト特徴",
            current_daily_tasks="テストタスク",
            recent_progress_feelings="テスト感情"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_summary(summary_data)
        
        assert exc_info.value.status_code == 404
        assert "Object with id 999 not found" in str(exc_info.value.detail)
    
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
        
        result = service.get_summary(999)
        
        assert result is None
    
    def test_get_summaries_by_object_id(self, db_session, sample_object):
        """オブジェクトIDでサマリー一覧取得テスト"""
        service = SummaryService(db_session)
        
        # 複数のサマリーを作成
        summary1 = SummaryCreate(
            object_id=sample_object.id,
            key_features="特徴1",
            current_daily_tasks="タスク1",
            recent_progress_feelings="感情1"
        )
        summary2 = SummaryCreate(
            object_id=sample_object.id,
            key_features="特徴2",
            current_daily_tasks="タスク2",
            recent_progress_feelings="感情2"
        )
        
        service.create_summary(summary1)
        # 少し待って異なるタイムスタンプを確保
        import time
        time.sleep(0.1)
        service.create_summary(summary2)
        
        query = SummaryQuery(object_id=sample_object.id, limit=10)
        result = service.get_summaries(query)
        
        assert len(result) == 2
        # 作成日時順でソートされているか確認（新しい順）
        assert result[0].created_at >= result[1].created_at
        assert all(summary.object_id == sample_object.id for summary in result)
    
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
        """存在しないサマリー更新テスト"""
        service = SummaryService(db_session)
        
        update_data = SummaryUpdate(key_features="更新された特徴")
        result = service.update_summary(999, update_data)
        
        assert result is None
    
    def test_delete_summary_success(self, db_session, sample_summary):
        """正常なサマリー削除テスト"""
        service = SummaryService(db_session)
        
        result = service.delete_summary(sample_summary.id)
        
        assert result is True
        
        # 削除されたか確認
        deleted_summary = service.get_summary(sample_summary.id)
        assert deleted_summary is None
    
    def test_delete_summary_not_found(self, db_session):
        """存在しないサマリー削除テスト"""
        service = SummaryService(db_session)
        
        result = service.delete_summary(999)
        
        assert result is False
    
    def test_summary_query_limit(self, db_session, sample_object):
        """サマリークエリのリミット機能テスト"""
        service = SummaryService(db_session)
        
        # 5つのサマリーを作成
        for i in range(5):
            summary_data = SummaryCreate(
                object_id=sample_object.id,
                key_features=f"特徴{i}",
                current_daily_tasks=f"タスク{i}",
                recent_progress_feelings=f"感情{i}"
            )
            service.create_summary(summary_data)
            # 少し待って異なるタイムスタンプを確保
            import time
            time.sleep(0.01)
        
        # リミット3で取得
        query = SummaryQuery(object_id=sample_object.id, limit=3)
        result = service.get_summaries(query)
        
        assert len(result) == 3
        # 作成日時順でソートされているか確認（新しい順）
        for i in range(len(result) - 1):
            assert result[i].created_at >= result[i + 1].created_at
    
    def test_summary_empty_query(self, db_session):
        """存在しないオブジェクトIDでのサマリー取得テスト"""
        service = SummaryService(db_session)
        
        query = SummaryQuery(object_id=999, limit=10)
        result = service.get_summaries(query)
        
        assert len(result) == 0 