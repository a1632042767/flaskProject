from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

db = SQLAlchemy()

# chrome_options = Options()
#
# chrome_options.add_experimental_option("prefs", {
#     "page.load.strategy": "eager"
# })
#
# chrome_options.add_argument("--disable-images")  # 禁止图片加载
# chrome_options.add_argument("--disable-javascript")  # 禁止js
# chrome_options.add_argument("--headless")  # 运行在无头模式
# chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
#
# driver_chrome = webdriver.Chrome(options=chrome_options)


# cors = CORS(resources={r'/*': {'origins': '*'}})
cors = CORS()

mail = Mail()