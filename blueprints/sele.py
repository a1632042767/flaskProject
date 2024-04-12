from urllib.parse import quote

from flask import Blueprint, request, jsonify, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from decorators import login_required
from models import UserInfoByBaidu
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from extension import db
import time
import requests

# 爬虫下载文库

bp = Blueprint("sele", __name__, url_prefix="/")


def getDataByBaidu(path):
    print("请求getDate")
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "page.load.strategy": "eager"
    })
    chrome_options.add_argument("--disable-images")  # 禁止图片加载
    chrome_options.add_argument("--disable-javascript")  # 禁止js
    chrome_options.add_argument("--headless")  # 运行在无头模式
    chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver_chrome = webdriver.Chrome(options=chrome_options)
    driver_chrome.set_page_load_timeout(5)
    print("配置驱动完成")

    docsData = []
    try:
        driver_chrome.get(path)
        print("请求网站成功")
        time.sleep(0.5)
        driver_chrome.refresh()
        docs = driver_chrome.find_elements(By.CSS_SELECTOR, '.list-item.doc-item-tile.layout-column')
        # titles = driver.find_elements(By.CLASS_NAME, 'tile-title')
        # contents = driver.find_elements(By.CLASS_NAME, 'tile-content')

        for doc in docs:
            docData = []
            link = doc.get_attribute("sula-resource-id")
            url = f'https://wenku.baidu.com/view/{link}.html'
            docData.append(url)
            title = doc.find_element(By.CLASS_NAME, 'tile-title').text
            docData.append(title)
            content = doc.find_element(By.CLASS_NAME, 'tile-content').text
            docData.append(content)
            pagetotal = doc.find_element(By.CLASS_NAME, 'pagetotal').text
            docData.append(pagetotal)
            # 判断是否需要vip
            try:
                doc.find_element(By.CLASS_NAME, 'vip-tag')
                isVip = True
            except NoSuchElementException:
                isVip = False

            docData.append(isVip)

            docsData.append(docData)
    except TimeoutException:
        return jsonify({
            "status": "false",
            "message": "访问网站超时"
        })

    driver_chrome.quit()
    return jsonify(docsData)


# 根据关键词查找
@bp.route("/search", methods=['GET', ])
def searchDocByName():
    searchDoc = request.args.get("searchDoc")
    searchDoc_encode = quote(searchDoc)
    searchUrl = f'https://wenku.baidu.com/search?word={searchDoc_encode}'
    docData = getDataByBaidu(searchUrl)

    return docData


# 百度文库
@login_required
@bp.route("/bdwk", methods=['GET', 'POST'])
def downloadDocInBaidu():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 运行在无头模式
    # chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)

    docPath = request.get_json().get("docPath")
    response = requests.get(docPath)
    if response.status_code == 200:
        user_id = session["user_id"]
        userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
        if userInfo:
            username = userInfo.username
            password = userInfo.password
            try:
                driver.get(docPath)
                time.sleep(2)
                userIcon = driver.find_element(By.CLASS_NAME, 'user-icon')

                if not userIcon:
                    # 登录
                    driver.find_element(By.CLASS_NAME, 'user-text').click()
                    usernameInput = (By.ID, 'TANGRAM__PSP_11__userName')
                    WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located(usernameInput))
                    driver.find_element(By.ID, 'TANGRAM__PSP_11__userName').send_keys(username)
                    driver.find_element(By.ID, 'TANGRAM__PSP_11__password').send_keys(password)
                    driver.find_element(By.ID, 'TANGRAM__PSP_11__isAgree').click()
                    driver.find_element(By.ID, 'TANGRAM__PSP_11__submit').send_keys(Keys.RETURN)
                    time.sleep(1)

                    if userIcon:
                        try:
                            guanggao = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div/div[2]/div[2]/div[5]')
                            guanggao.click()
                        except ElementNotInteractableException:
                            pass
                        # 如果成功
                        driver.find_element(By.CLASS_NAME, 'btn-normal-num').click()
                        time.sleep(2)
                        # 获取网站源码
                        page_source = driver.page_source
                        if "联合会员" in page_source:
                            return jsonify({
                                "status": "false",
                                "message": "该文档需要会员"
                            })

                    else:
                        return jsonify({
                            "status": "false",
                            "message": "登录失败，请检查用户名或密码"
                        })
                else:
                    try:
                        guanggao = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div/div[2]/div[2]/div[5]')
                        guanggao.click()
                    except ElementNotInteractableException:
                        pass

                    driver.find_element(By.CLASS_NAME, 'btn-normal-num').click()
                    time.sleep(2)
                    # 获取网站源码
                    page_source = driver.page_source
                    if "联合会员" in page_source:
                        return jsonify({
                            "status": "false",
                            "message": "该文档需要会员"
                        })
                    else:
                        return jsonify({
                            "status": "true",
                            "message": "下载成功, 已下载到浏览器默认下载目录"
                        })
            except TimeoutException:
                return jsonify({
                    "status": "false",
                    "message": "网页加载时间过长"
                })
            except NoSuchElementException:
                return jsonify({
                    "status": "false",
                    "message": "未找到该元素"
                })
        else:
            return jsonify({
                "status": "false",
                "message": "请先在个人中心处配置百度文库账密"
            })
    else:
        return jsonify({
            "status": "false",
            "message": "网页不存在或无法访问"
        })

# 豆丁
# @login_required
# @bp.route("/bdwk", methods=['GET', ])
# def downloadDocInDouding():
#     chrome_options = Options()
#     # chrome_options.add_argument("--headless")  # 运行在无头模式
#     # chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
#     driver = Chrome(options=chrome_options)
#     driver.set_page_load_timeout(10)
#
#     docPath = request.get_json().get("docPath")
#     driver.get(docPath)
#     driver.find_element(By.CLASS_NAME, "doc_down_btn").click()
