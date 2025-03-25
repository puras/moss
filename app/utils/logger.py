import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """配置应用日志"""
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件路径
    log_file = os.path.join(log_dir, 'app.log')
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(module)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    # 配置文件处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 配置控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # 配置应用日志器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)