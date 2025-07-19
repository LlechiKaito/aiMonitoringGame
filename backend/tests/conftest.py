import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# srcパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from utils.database import Base, get_db
from utils.db_models import ObjectDB, MemoryDB, SummaryDB
import pytz

# テスト用データベースの設定
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """テスト用のデータベースセッションを作成"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def sample_object(db_session):
    """テスト用のサンプルオブジェクトを作成"""
    obj = ObjectDB(
        name="テストオブジェクト",
        summary="テストサマリー",
        description="テスト用の説明",
        photos="[]"
    )
    db_session.add(obj)
    db_session.commit()
    db_session.refresh(obj)
    return obj

@pytest.fixture(scope="function")
def sample_memory(db_session, sample_object):
    """テスト用のサンプルメモリを作成"""
    from datetime import datetime
    memory = MemoryDB(
        object_id=sample_object.id,
        content="テストメモリ",
        importance=5,
        timestamp=datetime.now(pytz.timezone('Asia/Tokyo')),
        last_accessed=datetime.now(pytz.timezone('Asia/Tokyo'))
    )
    db_session.add(memory)
    db_session.commit()
    db_session.refresh(memory)
    return memory

@pytest.fixture(scope="function")
def sample_summary(db_session, sample_object):
    """テスト用のサンプルサマリーを作成"""
    from datetime import datetime
    summary = SummaryDB(
        object_id=sample_object.id,
        key_features="テスト特徴",
        current_daily_tasks="テストタスク",
        recent_progress_feelings="テスト感情",
        created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
    )
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)
    return summary 