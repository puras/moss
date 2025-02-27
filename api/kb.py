from flask import Blueprint, request
from database import get_db
from models.kb import KnowledgeBase, KnowledgeFile
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from utils.response import R
import os

kb_bp = Blueprint('kb', __name__)

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(BASE_DIR, 'knowledge_bases')
os.makedirs(KB_DIR, exist_ok=True)

@contextmanager
def get_session():
    db = next(get_db())
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

@kb_bp.route('/api/kb', methods=['GET'])
def list_kb():
    """列出所有知识库"""
    try:
        with get_session() as db:
            kbs = db.query(KnowledgeBase).all()
            return R.ok([{
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat()
            } for kb in kbs])
    except Exception as e:
        return R.fail(str(e))

@kb_bp.route('/api/kb/<int:kb_id>', methods=['GET'])
def get_kb(kb_id):
    """获取知识库信息"""
    try:
        with get_session() as db:
            kb = db.query(KnowledgeBase).filter_by(id=kb_id).first()
            if not kb:
                return R.fail("知识库不存在", 404)

            return R.ok({
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat()
            })
    except Exception as e:
        return R.fail(str(e))

@kb_bp.route('/api/kb', methods=['POST'])
def create_kb():
    """创建知识库"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return R.fail("知识库名称不能为空", 400)
            
        with get_session() as db:
            kb = KnowledgeBase(name=name, description=description)
            db.add(kb)
            db.flush()
            
            kb_path = os.path.join(KB_DIR, name)
            os.makedirs(kb_path, exist_ok=True)
            
            return R.ok({
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat()
            })
            
    except IntegrityError:
        return R.fail("知识库名称已存在", 400)
    except Exception as e:
        return R.fail(str(e))


@kb_bp.route('/api/kb/<int:kb_id>/update', methods=['POST'])
def update_kb(kb_id):
    """更新知识库信息"""
    try:
        data = request.get_json()
        with get_session() as db:
            kb = db.query(KnowledgeBase).filter_by(id=kb_id).first()
            if not kb:
                return R.fail("知识库不存在", 404)
                
            if 'description' in data:
                kb.description = data['description']
                
            return R.ok({
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "updated_at": kb.updated_at.isoformat()
            })
    except Exception as e:
        return R.fail(str(e))

@kb_bp.route('/api/kb/<int:kb_id>/delete', methods=['POST'])
def delete_kb(kb_id):
    """删除知识库"""
    try:
        with get_session() as db:
            kb = db.query(KnowledgeBase).filter_by(id=kb_id).first()
            if not kb:
                return R.fail("知识库不存在", 404)
                
            # 删除文件系统中的目录
            kb_path = os.path.join(KB_DIR, kb.name)
            if os.path.exists(kb_path):
                import shutil
                shutil.rmtree(kb_path)
                
            db.delete(kb)
            return R.ok(message="删除成功")
    except Exception as e:
        return R.fail(str(e))


@kb_bp.route('/api/kb/<int:kb_id>/files', methods=['GET'])
def list_files(kb_id):
    """列出知识库中的所有文件"""
    try:
        with get_session() as db:
            files = db.query(KnowledgeFile).filter_by(kb_id=kb_id).all()
            return R.ok([{
                    "id": f.id,
                    "filename": f.filename,
                    "file_type": f.file_type,
                    "created_at": f.created_at.isoformat()
                } for f in files])
    except Exception as e:
        return R.fail(str(e))

@kb_bp.route('/api/kb/<int:kb_id>/files', methods=['POST'])
def upload_file(kb_id):
    """上传文件到知识库"""
    try:
        with get_session() as db:
            kb = db.query(KnowledgeBase).filter_by(id=kb_id).first()
            if not kb:
                return R.fail("知识库不存在", 404)
                
            if 'file' not in request.files:
                return R.fail("没有文件", 400)

            file = request.files['file']
            if file.filename == '':
                return R.fail("没有选择文件", 400)
                
            # 保存文件
            kb_path = os.path.join(KB_DIR, kb.name)
            file_path = os.path.join(kb_path, file.filename)
            file.save(file_path)
            
            # 记录到数据库
            kb_file = KnowledgeFile(
                kb_id=kb_id,
                filename=file.filename,
                file_path=file_path,
                file_type=os.path.splitext(file.filename)[1]
            )
            db.add(kb_file)
            
            return R.ok({
                    "id": kb_file.id,
                    "filename": kb_file.filename,
                    "file_type": kb_file.file_type
                },
                message="文件上传成功")
    except Exception as e:
        return R.fail(str(e))

@kb_bp.route('/api/kb/<int:kb_id>/files/<int:file_id>/delete', methods=['POST'])
def delete_file(kb_id, file_id):
    """从知识库中删除文件"""
    try:
        with get_session() as db:
            kb_file = db.query(KnowledgeFile).filter_by(id=file_id, kb_id=kb_id).first()
            if not kb_file:
                return R.fail("文件不存在", 404)

            # 删除物理文件
            if os.path.exists(kb_file.file_path):
                os.remove(kb_file.file_path)
                
            db.delete(kb_file)
            return R.ok(message="文件删除成功")
    except Exception as e:
        return R.fail(str(e))
