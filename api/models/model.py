from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from models.base import Base


class Model(Base):
    __tablename__ = 'models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    permission = Column(String(50), default='private', nullable=False)  # private/public
    model_type = Column(String(50), nullable=False)  # 模型类型
    base_model = Column(String(100))  # 基础模型
    api_host = Column(String(200))  # API地址
    api_key = Column(String(200))  # API密钥
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class ModelType(Base):
    __tablename__ = 'model_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)