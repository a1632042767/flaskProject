import os

from flask import Blueprint, g, request, jsonify
from extension import db
from models import UserInfoByBaidu, BaiduCookie, User
from decorators import login_required
from sqlalchemy.exc import IntegrityError


bp = Blueprint("userinfo", __name__, url_prefix="/userinfo")


# 检查下载地址是否存在
def check_path(path):
    if os.path.isdir(path):
        return True
    else:
        return False


@bp.route("/setpath", methods=['POST'])
@login_required
def setDownloadPath():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    downloadPath = request.get_json().get("downloadPath")
    if not downloadPath:
        return jsonify({
            "status": "false",
            "message": "下载地址不能为空"
        })
    # 检查路径是否存在
    if check_path(downloadPath):
        user.downloadpath = downloadPath
        try:
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": "更新默认下载地址成功"
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "false",
                "message": "更新默认下载地址失败"
            })
    else:
        return jsonify({
            "status": "false",
            "message": "路径不存在，请重新输入"
        })


@bp.route("/setUserInfoBaidu", methods=['POST'])
@login_required
def setUserInfoBaidu():

    user_id = g.user.id

    user: User = User.query.get(user_id)
    userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
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
    if userInfo:
        userInfo.username = username
        userInfo.password = password

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

    try:
        db.session.add(newUserInfo)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "添加cookie成功"
        })
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "false",
            "message": "添加cookie失败"
        })


@bp.route("/getUserInfoBaidu", methods=['GET'])
@login_required
def getUserInfoBaidu():
    user_id = g.user.id
    print(user_id)
    # user_id = session.get('user_id')
    userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
    if userInfo:
        user_json = {
            "username": userInfo.username,
            "password": userInfo.password
        }

        response_json = {
            "status": "success",
            "message": "查询成功",
            "user": user_json
        }

        return jsonify(response_json)
    else:
        response_json = {
            "status": "success",
            "message": "查询成功"
        }
        return response_json


@bp.route("/setCookie", methods=['POST'])
@login_required
def setCookieBaidu():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    baiduCookie: BaiduCookie = BaiduCookie.query.get(user_id)
    cookie = request.get_json().get("cookie")

    if baiduCookie:
        baiduCookie.cookies = cookie
        try:
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "更新cookie成功"
            })
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "status": "false",
                "message": "更新cookie失败"
            })

    newBaiduCookie = BaiduCookie()
    newBaiduCookie.user = user
    newBaiduCookie.cookies = cookie

    try:
        db.session.add(newBaiduCookie)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "添加cookie成功"
        })
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "false",
            "message": "添加cookie失败"
        })
