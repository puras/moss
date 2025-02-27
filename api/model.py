from flask import Blueprint, request
from database import get_db
from models.model import Model
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from utils.response import R

model_bp = Blueprint('model', __name__)

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

@model_bp.route('/api/models', methods=['GET'])
def list_models():
    """获取模型列表"""
    try:
        with get_session() as db:
            models = db.query(Model).all()
            return R.ok([{
                "id": model.id,
                "name": model.name,
                "permission": model.permission,
                "model_type": model.model_type,
                "base_model": model.base_model,
                "api_host": model.api_host,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat()
            } for model in models])
    except Exception as e:
        return R.fail(str(e))

@model_bp.route('/api/models', methods=['POST'])
def create_model():
    """创建模型"""
    try:
        data = request.get_json()
        name = data.get('name')
        permission = data.get('permission', 'private')
        model_type = data.get('model_type')
        base_model = data.get('base_model')
        api_host = data.get('api_host')
        api_key = data.get('api_key')
        
        if not name or not model_type:
            return R.fail("模型名称和类型不能为空", 400)
            
        with get_session() as db:
            model = Model(
                name=name,
                permission=permission,
                model_type=model_type,
                base_model=base_model,
                api_host=api_host,
                api_key=api_key
            )
            db.add(model)
            db.flush()
            
            return R.ok({
                "id": model.id,
                "name": model.name,
                "permission": model.permission,
                "model_type": model.model_type,
                "base_model": model.base_model,
                "api_host": model.api_host,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat()
            })
            
    except IntegrityError:
        return R.fail("模型名称已存在", 400)
    except Exception as e:
        return R.fail(str(e))

@model_bp.route('/api/models/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """获取模型详情"""
    try:
        with get_session() as db:
            model = db.query(Model).filter_by(id=model_id).first()
            if not model:
                return R.fail("模型不存在", 404)
                
            return R.ok({
                "id": model.id,
                "name": model.name,
                "permission": model.permission,
                "model_type": model.model_type,
                "base_model": model.base_model,
                "api_host": model.api_host,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat()
            })
    except Exception as e:
        return R.fail(str(e))

@model_bp.route('/api/models/<int:model_id>/update', methods=['POST'])
def update_model(model_id):
    """更新模型"""
    try:
        data = request.get_json()
        with get_session() as db:
            model = db.query(Model).filter_by(id=model_id).first()
            if not model:
                return R.fail("模型不存在", 404)
            
            if 'permission' in data:
                model.permission = data['permission']
            if 'model_type' in data:
                model.model_type = data['model_type']
            if 'base_model' in data:
                model.base_model = data['base_model']
            if 'api_host' in data:
                model.api_host = data['api_host']
            if 'api_key' in data:
                model.api_key = data['api_key']
                
            return R.ok({
                "id": model.id,
                "name": model.name,
                "permission": model.permission,
                "model_type": model.model_type,
                "base_model": model.base_model,
                "api_host": model.api_host,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat()
            })
    except Exception as e:
        return R.fail(str(e))

@model_bp.route('/api/models/<int:model_id>/delete', methods=['POST'])
def delete_model(model_id):
    """删除模型"""
    try:
        with get_session() as db:
            model = db.query(Model).filter_by(id=model_id).first()
            if not model:
                return R.fail("模型不存在", 404)
                
            db.delete(model)
            return R.ok(message="删除成功")
    except Exception as e:
        return R.fail(str(e))