from functools import wraps
from flask import g, redirect, url_for


# 登陆装饰器
# TODO 返回登录界面还没有做
def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if g.user:
            func(*args, **kwargs)
        else:
            return redirect(url_for("auth.login"))
    return inner
