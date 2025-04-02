import pytest
from bak.app import create_app
from bak.app.extensions import db
from bak.app.models.ucenter.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        return user