from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_bases'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    files = relationship("KnowledgeFile", back_populates="knowledge_base", cascade="all, delete-orphan")

class KnowledgeFile(Base):
    __tablename__ = 'knowledge_files'
    
    id = Column(Integer, primary_key=True)
    kb_id = Column(Integer, ForeignKey('knowledge_bases.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="files")