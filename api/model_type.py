from flask import Blueprint, request
from database import get_db
from models.model import ModelType
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from utils.response import R

model_type_bp = Blueprint('model_type', __name__)

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

@model_type_bp.route('/api/model-types', methods=['GET'])
def list_model_types():
    """获取模型类型列表"""
    try:
        with get_session() as db:
            types = db.query(ModelType).all()
            return R.ok([{
                "id": type.id,
                "name": type.name,
                "code": type.code,
                "description": type.description,
                "created_at": type.created_at.isoformat(),
                "updated_at": type.updated_at.isoformat()
            } for type in types])
    except Exception as e:
        return R.fail(str(e))

@model_type_bp.route('/api/model-types', methods=['POST'])
def create_model_type():
    """创建模型类型"""
    try:
        data = request.get_json()
        name = data.get('name')
        code = data.get('code')
        description = data.get('description', '')
        
        if not name or not code:
            return R.fail("名称和编码不能为空", 400)
            
        with get_session() as db:
            model_type = ModelType(
                name=name,
                code=code,
                description=description
            )
            db.add(model_type)
            db.flush()
            
            return R.ok({
                "id": model_type.id,
                "name": model_type.name,
                "code": model_type.code,
                "description": model_type.description,
                "created_at": model_type.created_at.isoformat(),
                "updated_at": model_type.updated_at.isoformat()
            })
            
    except IntegrityError:
        return R.fail("名称或编码已存在", 400)
    except Exception as e:
        return R.fail(str(e))

@model_type_bp.route('/api/model-types/<int:type_id>', methods=['GET'])
def get_model_type(type_id):
    """获取模型类型详情"""
    try:
        with get_session() as db:
            model_type = db.query(ModelType).filter_by(id=type_id).first()
            if not model_type:
                return R.fail("模型类型不存在", 404)
                
            return R.ok({
                "id": model_type.id,
                "name": model_type.name,
                "code": model_type.code,
                "description": model_type.description,
                "created_at": model_type.created_at.isoformat(),
                "updated_at": model_type.updated_at.isoformat()
            })
    except Exception as e:
        return R.fail(str(e))

@model_type_bp.route('/api/model-types/<int:type_id>/update', methods=['POST'])
def update_model_type(type_id):
    """更新模型类型"""
    try:
        data = request.get_json()
        with get_session() as db:
            model_type = db.query(ModelType).filter_by(id=type_id).first()
            if not model_type:
                return R.fail("模型类型不存在", 404)
            
            if 'name' in data:
                model_type.name = data['name']
            if 'code' in data:
                model_type.code = data['code']
            if 'description' in data:
                model_type.description = data['description']
                
            return R.ok({
                "id": model_type.id,
                "name": model_type.name,
                "code": model_type.code,
                "description": model_type.description,
                "created_at": model_type.created_at.isoformat(),
                "updated_at": model_type.updated_at.isoformat()
            })
    except IntegrityError:
        return R.fail("名称或编码已存在", 400)
    except Exception as e:
        return R.fail(str(e))

@model_type_bp.route('/api/model-types/<int:type_id>/delete', methods=['POST'])
def delete_model_type(type_id):
    """删除模型类型"""
    try:
        with get_session() as db:
            model_type = db.query(ModelType).filter_by(id=type_id).first()
            if not model_type:
                return R.fail("模型类型不存在", 404)
                
            db.delete(model_type)
            return R.ok(message="删除成功")
    except Exception as e:
        return R.fail(str(e))