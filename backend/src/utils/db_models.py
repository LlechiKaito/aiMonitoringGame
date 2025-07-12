from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class ObjectDB(Base):
    __tablename__ = "objects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    description = Column(String, nullable=False)
    photos = Column(Text, default="[]")  # JSON文字列として多次元配列を保存
    
    # リレーションシップ
    memories = relationship("MemoryDB", back_populates="object")
    summaries = relationship("SummaryDB", back_populates="object")

class MemoryDB(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    content = Column(String, nullable=False)
    importance = Column(Float, default=0.5)
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    object = relationship("ObjectDB", back_populates="memories")

class SummaryDB(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    object_id = Column(Integer, ForeignKey("objects.id"), nullable=False)
    key_features = Column(String, nullable=False)
    current_daily_tasks = Column(String, nullable=False)
    recent_progress_feelings = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    object = relationship("ObjectDB", back_populates="summaries") 