import wtforms
from wtforms.validators import Email, Length, EqualTo
from models import User, EmailCode
from extension import db
from sqlalchemy import desc


class RegisterForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])
    code = wtforms.StringField(validators=[Length(min=4, max=4, message="验证码格式错误！")])
    username = wtforms.StringField(validators=[Length(min=4, max=20, message="用户名长度4-20位！")])
    password = wtforms.StringField(validators=[Length(min=6, max=12, message="密码长度6-12位！")])
    confirmPassword = wtforms.StringField(validators=[EqualTo("password", message="两次密码不一致！")])

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            raise wtforms.ValidationError(message="该邮箱已被注册")

    def validate_code(self, field):
        code = field.data
        email = self.email.data
        code = EmailCode.query.filter_by(email=email, code=code).first()
        if not code:
            raise wtforms.ValidationError(message="邮箱或验证码错误")

    def validate_username(self, field):
        username = field.data
        user = User.query.filter_by(username=username).first()
        if user:
            raise wtforms.ValidationError(message="用户名重复！")


class LoginForm(wtforms.Form):
    username = wtforms.StringField(validators=[Length(min=4, max=20, message="用户名长度4-12位")])
    # password = wtforms.StringField(validators=[Length(min=6, max=12, message="password length 6-12")])
    password = wtforms.StringField(validators=[Length(min=6, max=12, message="密码长度6-12位")])
