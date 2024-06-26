from urllib.parse import quote

from flask import Flask, render_template, session, g
from extension import db, cors, mail
from blueprints.auth import bp as auth_bp
from blueprints.sele import bp as sele_bp
from blueprints.seleDD import bp as seleDD_bp
from blueprints.admin import bp as admin_bp
from blueprints.userInfo import bp as userInfo_bp
from flask_migrate import Migrate
from models import User
import config
from decorators import login_required

app = Flask(__name__)
# 导入配置文件
cors.init_app(app)
app.config.from_object(config)
db.init_app(app)
mail.init_app(app)

migrate = Migrate(app, db)


# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(sele_bp)
app.register_blueprint(seleDD_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(userInfo_bp)


# @app.route('/')
# def hello_world():
#     return "hello"


############# 错误页面

@app.errorhandler(404)
def error_404(err):
    return render_template('404.html')


@app.errorhandler(500)
def error_500(err):
    return render_template('500.html')


##############

# 自动提取用户信息，如果未登录则设置为None，g为全局对象
@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)


# 根据关键词查找

# 上下文变量只有使用flask本身的模版的时候才有用
# # 设置上下文变量
# @app.context_processor
# def my_context_processor():
#     return {"user": g.user}


# return render_template('../../flask-web/public/index.html')

# @app.route('/<path:fallback>')
# def fallback(fallback):  # Vue Router 的 mode 为 'hash' 时可移除该方法
#     if fallback.startswith('css/') or fallback.startswith('js/') \
#             or fallback.startswith('img/') or fallback == 'favicon.ico':
#         return app.send_static_file(fallback)
#     else:
#         return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(debug=True)
