from flask import Blueprint, jsonify, redirect, request, url_for, session
from extension import mail, db
from flask_mail import Message
from models import EmailCode
import random
import string
from .forms import RegisterForm, LoginForm
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

# 认证


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=['POST', ])
def login():
    req_data = request.get_json()
    form = LoginForm()
    form.username.data = req_data.get("username")
    form.password.data = req_data.get("password")

    if form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({
                "status": "false",
                "message": "用户不存在！"
                # "data": None
            })
        if check_password_hash(user.password, password):
            if username == 'admin1':
                session['is_admin'] = True

            user_json = {
                "id": user.id,
                "username": user.username
            }
            session['user_id'] = user.id
            response_json = {
                "status": "success",
                "message": "登录成功",
                "user": user_json
            }
            return jsonify(response_json)

            # return redirect("首页")
        else:
            return jsonify({
                "status": "false",
                "message": "用户名或密码错误！"
            })

    else:
        errors = {}
        for field_name, field_errors in form.errors.items():
            # 假设每个字段只有一个错误信息，取第一个
            errors[field_name] = field_errors[0]
        print(errors)
        return jsonify({'status': 'false', 'message': errors})


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return "注册页面"
    else:
        req_data = request.get_json()
        form = RegisterForm()
        form.username.data = req_data.get("username")
        form.password.data = req_data.get("password")
        form.email.data = req_data.get("email")
        form.confirmPassword.data = req_data.get("confirmPassword")
        form.code.data = req_data.get("code")

        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            code = form.code.data
            # generate_password_hash 密码hash加密
            try:
                newUser = User(email=email, username=username, password=generate_password_hash(password))
                code = EmailCode.query.filter_by(email=email, code=code).first()
                db.session.add(newUser)
                # 删除验证码
                db.session.delete(code)

                db.session.commit()
                # 注意跳转不是login而是auth.login
                return jsonify({
                    "status": "success",
                    "message": "注册成功",
                })
                # , redirect(url_for("auth.login"))
            except Exception as e:
                print(e)
                return jsonify({
                    "status": "false",
                    "message": "注册失败！",
                })
        else:
            # form.error()报错信息为字典格式，将其转换为json格式
            errors = {}
            for field_name, field_errors in form.errors.items():
                # 假设每个字段只有一个错误信息，取第一个
                errors[field_name] = field_errors[0]
            # print(errors)
            return jsonify({'status': 'false', 'message': errors})


@bp.route("/sendmail", methods=['POST', ])
def send_mail():
    email = request.get_json().get("email")
    if not email:
        return jsonify({
            "status": "false",
            "message": "未输入邮箱"
        })
    source = string.digits * 4
    code = random.sample(source, 4)
    # random生成的是数组，使用join将生成的列表改为正常的4个数字，""可以使用分隔符，为空表示不分隔
    code = "".join(code)
    try:
        message = Message(subject="文库下载注册", sender=("文库下载", "1632042767@qq.com"), recipients=[email],
                          body=f"您的验证码为{code}")
        mail.send(message)
        emailCode = EmailCode(email=email, code=code)
        db.session.add(emailCode)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "验证码发送成功"
            # "data": None
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": "false",
            "message": "验证码发送失败(邮箱地址不存在)",
            # "data": None
        })

# @bp.route("/mail/test")
# def mail_test():
#     message = Message(subject="test", recipients=["1632042767@qq.com"], body="测试邮件")
#     mail.send(message)
#     return "邮件发送成功"
