from datetime import datetime
from flask import jsonify

class R:
    @staticmethod
    def ok(data=None, message="请求成功"):
        return jsonify({
            "code": 0,
            "message": message,
            "data": data,
            "timestamp": datetime.now().timestamp()
        })
    
    @staticmethod
    def fail(message="请求失败", code=500):
        return jsonify({
            "code": code,
            "message": message,
            "data": None,
            "timestamp": datetime.now().timestamp()
        }), code