import os
from urllib.parse import quote

from flask import Blueprint, request, jsonify, g
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from sqlalchemy.exc import IntegrityError

from decorators import login_required
from models import UserInfoDouding, User
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from extension import db
import requests
import time

bp = Blueprint("seleDouding", __name__, url_prefix="/dd")


def getDataByDouding():
    pass


def loginDouding():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 运行在无头模式
    chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)

    user_id = g.user.id
    userInfo: UserInfoDouding = UserInfoDouding.query.get(user_id)
    if userInfo:
        username = userInfo.username
        password = userInfo.password
        try:
            driver.get("https://www.docin.com/")
            print("请求网站成功")

        except TimeoutException:
            return jsonify({
                "status": "false",
                "message": "网站或某一标签加载时间过长"
            })



