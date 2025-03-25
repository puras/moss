from flask import Flask, request
from sqlalchemy.exc import SQLAlchemyError

from app.config import config
from app.extensions import db, migrate, jwt, cors
from time import time

from app.utils.logger import setup_logger

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 配置日志
    setup_logger(app)
    
    # 初始化扩展
    register_extensions(app)

    # 注册API蓝图
    register_blueprints(app)

    # 注册错误处理
    register_error_handlers(app)
    
    # 注册请求日志
    register_request_logging(app)
    
    return app

def register_request_logging(app):
    @app.before_request
    def start_timer():
        request.start_time = time()

    @app.after_request
    def log_request(response):
        # 如果是静态文件请求，不记录日志
        if request.path.startswith('/static'):
            return response
            
        # 计算请求处理时间
        duration = time() - request.start_time
        
        # 获取请求数据
        request_data = request.get_json() if request.is_json else None

        # 获取响应数据
        response_data = response.get_json() if response.is_json else None
        
        # 构建日志信息
        log_data = {
            'method': request.method,
            'path': request.path,
            'status': response.status_code,
            'duration': f'{duration:.2f}s',
            'ip': request.remote_addr,
            'request_data': request_data,
            'response_data': response_data
        }
        
        # 记录日志
        app.logger.info(f"Request: {log_data}")
        
        return response

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

def register_blueprints(app):
    from app.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    # 打印蓝图信息
    if app.debug:
        print("\n已注册的URLMap:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} [{','.join(rule.methods)}]")

def register_error_handlers(app):
    from app.utils.response import R

    @app.errorhandler(404)
    def handle_404_error(e):
        return R.not_found("Not found")
        
    @app.errorhandler(500)
    def handle_500_error(e):
        app.logger.debug(str(e))
        return R.fail("Internal server error")

    # 注册全局错误处理器
    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        app.logger.debug("SQLAlchemyError", error)
        return R.fail("数据库操作错误")