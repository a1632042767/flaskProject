
# session密钥
SECRET_KEY = "asdwdasfasdas;s"

# 数据库配置信息

HOSTNAME = '127.0.0.1'
PORT     = '3306'
DATABASE = 'finallydesign'
USERNAME = 'root'
PASSWORD = 'root'
DB_URI   = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI


# 邮箱配置
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "1632042767@qq.com"
MAIL_PASSWORD = "qwihxamrbxuldijf"
MAIL_DEFAULT_SENDER = "1632042767@qq.com"
