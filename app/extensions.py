from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 初始化扩展，但不绑定到特定的应用实例
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()