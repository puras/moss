from flask import Flask
from database import init_db
from kb import kb_bp
from model import model_bp
from model_type import model_type_bp
from prompt import prompt_bp

app = Flask(__name__)

# 初始化数据库
init_db()

# 注册蓝图
app.register_blueprint(kb_bp)
app.register_blueprint(model_bp)
app.register_blueprint(model_type_bp)
app.register_blueprint(prompt_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
