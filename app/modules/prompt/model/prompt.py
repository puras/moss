from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.db.base import Base

class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    content = Column(Text, nullable=False)
    tags = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PromptOptimizerTemplate(Base):
    __tablename__ = "prompt_optimizer_template"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    temp_type = Column(String(100), nullable=False)
    builtin = Column(Boolean, default=True)
    description = Column(String(500))