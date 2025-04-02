import time

from flask import jsonify

class R:
    @staticmethod
    def ok(data=None, message="Success", code=200):
        """"""
        return R.response(data, message, code)

    @staticmethod
    def fail(message="Failure", code=500, errors=None):
        """

        """
        if errors is None:
            return R.response(code=code, message=message, status=False)
        else:
            return R.response(code=code, message=message, status=False, errors=errors)

    @staticmethod
    def not_found(message="资源不存在"):
        return R.fail(message, 404)

    @staticmethod
    def bad_request(message="请求参数错误", errors=None):
        return R.fail(message, 400, errors=errors)


    @staticmethod
    def server_error(message="服务器内部错误"):
        return R.fail(message, 500)

    @staticmethod
    def response(data=None, message="Success", code=200, status=True, **kwargs):
        """
        标准API响应格式
        
        Args:
            data: 返回的数据
            message: 响应消息
            code: 状态码
            status: 请求是否成功
            **kwargs: 其他元数据
        
        Returns:
            JSON格式的响应
        """
        response = {
            "code": code,
            "message": message,
            "status": status,
            "data": data,
            "timestamp": time.time()
        }

        # 添加其他元数据
        if kwargs:
            for key, value in kwargs.items():
                response[key] = value

        return jsonify(response), code