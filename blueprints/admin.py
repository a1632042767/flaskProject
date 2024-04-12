from flask import Blueprint, session, request, jsonify, abort
from apiMap.UserApi import UserApi
from models import User
from decorators import login_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


# def is_admin_user():
#     # 检查session中是否有is_admin字段，并且其值为True
#     return 'is_admin' in session and session['is_admin']
#
#
# @bp.route("/", methods=['GET'])
# @login_required
# def admin():
#     if not is_admin_user():
#         abort(403)
#     else:
#         return jsonify({
#             "code": 200
#         })


# user_view = UserApi.as_view('user.api') 因为在蓝图中已经添加过前缀了，所以不能使用user.adi的命名方式
user_view = UserApi.as_view('api')
bp.add_url_rule('/users/', defaults={'id': None}, view_func=user_view, methods=['GET', ])
bp.add_url_rule('/users', view_func=user_view, methods=['POST', ])
bp.add_url_rule('/users/<int:id>', view_func=user_view, methods=['GET', "PUT", "DELETE"])
