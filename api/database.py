from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# 创建 db 目录
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
os.makedirs(DB_DIR, exist_ok=True)

# 配置数据库连接
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'knowledge_base.db')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()