import os

from flask import Blueprint, g, request, jsonify

from extension import db
from models import UserInfoByBaidu, User, UserInfoDouding
from decorators import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError


bp = Blueprint("userinfo", __name__, url_prefix="/userinfo")


# 检查下载地址是否存在
def check_path(path):
    if os.path.isdir(path):
        return True
    else:
        return False


@bp.route("/updatePassword", methods=['POST', ])
def updatePassword():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    oldPassword = request.get_json().get("old")
    newPassword = request.get_json().get("new")
    newPassword1 = request.get_json().get("new1")

    if newPassword != newPassword1:
        return jsonify({
            "status": "false",
            "message": "两次密码不一致！"
        })

    if check_password_hash(user.password, oldPassword):
        user.password = generate_password_hash(newPassword)
        try:
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "更改密码成功"
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "false",
                "message": "更改密码失败"
            })


@bp.route("/getUserInfo", methods=['GET'])
@login_required
def getUserInfo():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    userInfoBd: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
    userInfoDd: UserInfoDouding = UserInfoDouding.query.get(user_id)

    user_info = {
        "downloadPath": user.downloadpath,
        "usernameBd": getattr(userInfoBd, 'username', None),
        "passwordBd": getattr(userInfoBd, 'password', None),
        "cookiesBd": getattr(userInfoBd, 'cookies', None),
        "usernameDd": getattr(userInfoDd, 'username', None),
        "passwordDd": getattr(userInfoDd, 'password', None),
        "cookiesDd": getattr(userInfoDd, 'cookies', None),
    }

    user_info = {k: v for k, v in user_info.items() if v is not None}
    # print(user_info)

    return jsonify({
        "status": "success",
        "message": "查询成功",
        "userinfo": user_info
    })


@bp.route("/setself", methods=['POST'])
@login_required
def setDownloadPathAndUsername():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    downloadPath = request.get_json().get("downloadPath")
    username = request.get_json().get("username")
    if not username:
        return jsonify({
            "status": "false",
            "message": "用户名不能为空"
        })
    if not downloadPath:
        return jsonify({
            "status": "false",
            "message": "下载地址不能为空"
        })

    checkUser = User.query.filter_by(username=username).first()
    if checkUser and checkUser.id != id:
        return {
            'status': 'false',
            'message': '用户名重复！'
        }

    # 检查路径是否存在
    if check_path(downloadPath):
        user.username = username
        user.downloadpath = downloadPath
        try:
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "更新数据成功"
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "false",
                "message": "更新数据失败"
            })
    else:
        return jsonify({
            "status": "false",
            "message": "路径不存在，请重新输入"
        })


@bp.route("/setUserInfoBd", methods=['POST'])
@login_required
def setUserInfoBaidu():

    user_id = g.user.id

    user: User = User.query.get(user_id)
    userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
    username = request.get_json().get("username")
    password = request.get_json().get("password")
    cookies = request.get_json().get("cookies")
    if not username:
        return jsonify({
            "status": "false",
            "message": "用户名不能为空"
        })
    if not password:
        return jsonify({
            "status": "false",
            "message": "密码不能为空"
        })
    if userInfo:
        userInfo.username = username
        userInfo.password = password
        if cookies:
            userInfo.cookies = cookies
        try:
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "更新百度账密成功"
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "false",
                "message": "更新百度账密失败"
            })

    newUserInfo = UserInfoByBaidu()
    newUserInfo.user = user
    newUserInfo.username = username
    newUserInfo.password = password
    if cookies:
        newUserInfo.cookies = cookies
    try:
        db.session.add(newUserInfo)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "添加数据成功"
        })
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "false",
            "message": "添加数据失败"
        })


@bp.route("/setUserInfoDd", methods=['POST'])
@login_required
def setUserInfoDouding():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    userInfo: UserInfoDouding = UserInfoDouding.query.get(user_id)
    cookies = request.get_json().get("cookies")
    username = request.get_json().get("username")
    password = request.get_json().get("password")

    if not username:
        return jsonify({
            "status": "false",
            "message": "用户名不能为空"
        })
    if not password:
        return jsonify({
            "status": "false",
            "message": "密码不能为空"
        })

    newUserInfo = UserInfoDouding()

    if userInfo:
        userInfo.username = username
        userInfo.password = password

        if cookies:
            userInfo.cookies = cookies

        try:
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "更新豆丁账密成功"
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "false",
                "message": "更新豆丁账密失败"
            })

    newUserInfo.user = user
    newUserInfo.username = username
    newUserInfo.password = password
    if cookies:
        newUserInfo.cookies = cookies
    try:
        db.session.add(newUserInfo)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "添加数据成功"
        })
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "false",
            "message": "添加数据失败"
        })


# @bp.route("/getUserInfoBaidu", methods=['GET'])
# @login_required
# def getUserInfoBaidu():
#     user_id = g.user.id
#     print(user_id)
#     # user_id = session.get('user_id')
#     userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
#     if userInfo:
#         user_json = {
#             "username": userInfo.username,
#             "password": userInfo.password,
#             "cookies": userInfo.cookies
#         }
#
#         response_json = {
#             "status": "success",
#             "message": "查询成功",
#             "user": user_json
#         }
#
#         return jsonify(response_json)
#     else:
#         response_json = {
#             "status": "success",
#             "message": "查询成功"
#         }
#         return jsonify(response_json)
#
#
# def getUserInfoDouding():
#     user_id = g.user.id
#     userInfo: UserInfoDouding = UserInfoDouding.query.get(user_id)
#
#     if userInfo:
#         user_json = {
#             "username": userInfo.username,
#             "password": userInfo.password,
#             "cookies": userInfo.cookies
#         }
#
#         response_json = {
#             "status": "success",
#             "message": "查询成功",
#             "user": user_json
#         }
#
#         return jsonify(response_json)
#     else:
#         response_json = {
#             "status": "success",
#             "message": "查询成功"
#         }
#         return jsonify(response_json)
#

