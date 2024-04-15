from functools import wraps
from flask import g, jsonify


# 登陆装饰器
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        else:
            return jsonify({
                "status": "none",
                "message": "用户未登录"
            })
    return inner
