from flask import Blueprint, jsonify, request
from models.model import Prompt
from database import session

prompt_bp = Blueprint('prompt', __name__, url_prefix='/prompts')

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

@prompt_bp.route('', methods=['GET'])
def get_prompt_templates():
    prompts = session.query(Prompt).all()
    return R.ok([{
        'id': t.id,
        'name': t.name,
        'content': t.content,
        'description': t.description,
        'model_id': t.model_id,
        'created_at': t.created_at.isoformat(),
        'updated_at': t.updated_at.isoformat()
    } for t in prompts])

@prompt_bp.route('', methods=['POST'])
def create_prompt_template():
    data = request.json
    prompt = Prompt(
        name=data['name'],
        content=data['content'],
        description=data.get('description')
    )
    session.add(prompt)
    session.commit()
    return jsonify({
        'id': prompt.id,
        'message': 'Prompt  created successfully'
    }), 201

@prompt_bp.route('/<int:prompt_id>', methods=['PUT'])
def update_prompt_template(prompt_id):
    prompt = session.query(Prompt).get(prompt_id)
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    data = request.json
    prompt.name = data.get('name', prompt.name)
    prompt.content = data.get('content', prompt.content)
    prompt.description = data.get('description', prompt.description)
    session.commit()
    return jsonify({
        'id': prompt.id,
        'message': 'Prompt updated successfully'
    })

@prompt_bp.route('/<int:prompt_id>', methods=['DELETE'])
def delete_prompt_template(prompt_id):
    prompt = session.query(Prompt).get(prompt_id)
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    session.delete(prompt)
    session.commit()
    return jsonify({'message': 'Prompt deleted successfully'})
