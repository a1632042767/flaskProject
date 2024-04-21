import os
import re
from urllib.parse import quote

import requests
import time

from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify, g

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, \
    ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from sqlalchemy.exc import IntegrityError

from decorators import login_required
from models import UserInfoDouding, User
from extension import db

bp = Blueprint("seleDouding", __name__, url_prefix="/dd")

findLink = re.compile(r'href="(/p-\d+\.html)"')
findTitle = re.compile(r'target="_cygj" title="(.*?)"')


@bp.route("/search", methods=['GET', ])
# @login_required
def getDataByDouding():
    searchDoc = request.args.get("searchDoc")
    searchDoc_encode = quote(searchDoc)
    basePath = f'https://www.docin.com/search.do?nkey={searchDoc_encode}'
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 运行在无头模式
    chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)

    driver.get(basePath)
    try:
        yanzheng = driver.find_element(By.CLASS_NAME, "dialogTitle")
        return jsonify({
            "status": "false",
            "message": "需要验证！"
        })
    except NoSuchElementException:
        pass

    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        # "Cookie": cookies,
    }

    docsData = []
    for i in range(0, 5):
        path = basePath + f'&currentPage={i}'
        print(path)

        response = requests.get(path, headers=head)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        try:
            div_element = soup.find('div', class_='doc-list-style2 doc-mark')
            for doc in div_element.find_all('dl', class_="clear"):
                data = []
                try:
                    pageTotal = doc.find('span', class_="pageno").get_text()
                    if pageTotal:
                        data.append(pageTotal)
                    content = doc.find('dd', class_="summary").get_text()
                    if content:
                        data.append(content)
                    # print(doc)
                except AttributeError:
                    pass
                doc = str(doc)
                try:
                    link = re.findall(findLink, doc)[0]
                    if link:
                        link = f"https://www.docin.com{link}"
                        data.append(link)
                    title = re.findall(findTitle, doc)[0]
                    if title:
                        # print(title)
                        data.append(title)
                except IndexError:
                    pass

                docsData.append(data)

        except AttributeError:
            return jsonify({
                "status": "false",
                "message": "出现错误"
            })

        # print(docsData)

    return jsonify({
        "status": "success",
        "message": "请求成功",
        "docsData": docsData
    })




@bp.route("/ddwk", methods=['POST', ])
@login_required
def downloadDocInDouding():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    # download_dir = r"C:\\"
    download_dir = user.downloadpath
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # 运行在无头模式
    chrome_options.add_argument("--disable-images")  # 禁止图片加载
    chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)

    docPath = request.get_json().get("docPath")

    try:
        initial_files = os.listdir(download_dir)

        driver.get(docPath)
        print("请求网站成功")
        # time.sleep(1)
        userInfo: UserInfoDouding = UserInfoDouding.query.get(user_id)
        if userInfo.cookies:
            cookies = userInfo.cookies

            for cookie in cookies:
                cookie = cookie.strip()
                cookie_name, cookie_value = cookie.split("=", maxsplit=1)
                driver.add_cookie({'name': cookie_name, 'value': cookie_value})

            driver.refresh()
            print("网站刷新成功")

            head_pic = driver.find_element(By.CLASS_NAME, 'head_pic')
            if not head_pic:
                response = loginDouding()
                try:
                    responseData = response.get_json()
                    return responseData
                except Exception as e:
                    print(e)
                    for cookie in response:
                        driver.add_cookie(cookie)

                    driver.refresh()

        else:
            response = loginDouding()
            try:
                responseData = response.get_json()
                return responseData
            except Exception as e:
                print(e)
                for cookie in response:
                    driver.add_cookie(cookie)

            driver.refresh()

        try:
            dingyue = driver.find_element(By.XPATH, '/html/body/div[16]/div/div/div[1]/a')
            dingyue.click()
        except ElementNotInteractableException:
            pass
        except NoSuchElementException:
            pass

        downloadButton = (By.CLASS_NAME, 'doc_down_btn')
        WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(downloadButton))

        try:
            driver.find_element(By.CLASS_NAME, 'doc_down_btn').click()
            time.sleep(5)

            final_files = os.listdir(download_dir)
            new_files = set(final_files) - set(initial_files)

            page_source = driver.page_source
            if "直接购买" in page_source:
                driver.quit()
                return jsonify({
                    "status": "false",
                    "message": "该文档需要购买"
                })

            else:
                if new_files:
                    driver.quit()
                    return jsonify({
                        "status": "true",
                        "message": f"下载成功, 已下载到默认下载目录{download_dir}"
                    })
                else:
                    return jsonify({
                        "status": "flase",
                        "message": "未下载成功"
                    })

        except ElementNotInteractableException:
            return jsonify({
                "status": "false",
                "message": "下载按钮无法点击"
            })

    except TimeoutException:
        driver.quit()
        return jsonify({
            "status": "false",
            "message": "网页加载时间过长"
        })


@bp.route("/logindd", methods=['POST', ])
@login_required
def loginDouding():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 运行在无头模式
    # chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
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

            loginButton = (By.XPATH, '/html/body/div[2]/div/div[3]/div/div/a[1]')
            WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(loginButton))
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div/div/a[1]').click()
            usernameInput = (By.ID, 'username_new')
            WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located(usernameInput))

            driver.find_element(By.ID, 'username_new').send_keys(username)
            driver.find_element(By.ID, 'password_new').send_keys(password)
            driver.find_element(By.CSS_SELECTOR, '.btn.loginBtn').click()
            print("点击登陆成功")

            time.sleep(1)

            try:
                yanzheng = driver.find_element(By.ID, 'username_new')
                print("需要验证")
                return jsonify({
                    "status": "false",
                    "message": "豆丁登录需要验证"
                })
            except ElementNotInteractableException:
                pass
            except NoSuchElementException:
                pass

            if usernameInput:
                print("用户名密码错误")
                return jsonify({
                    "status": "false",
                    "message": "用户名或密码错误"
                })

            try:
                dingyue = driver.find_element(By.XPATH, '/html/body/div[16]/div/div/div[1]/a')
                dingyue.click()
            except ElementNotInteractableException:
                pass
            except NoSuchElementException:
                pass

            cookies = driver.get_cookies()

            # 转换cookie格式
            cookie_str = ""
            for cookie in cookies:
                cookie_name = cookie['name']
                cookie_value = cookie['value']
                cookie_str += f"{cookie_name}={cookie_value}; "

            userInfo.cookies = cookie_str
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return jsonify({
                    "status": "false",
                    "message": "向表中添加cookie失败"
                })

            driver.quit()
            return cookies

        except UnexpectedAlertPresentException:
            return jsonify({
                "status": "false",
                "message": "用户名或密码错误"
            })

        except TimeoutException:
            return jsonify({
                "status": "false",
                "message": "网站或某一标签加载时间过长"
            })

        except ElementClickInterceptedException:
            return jsonify({
                "status": "false",
                "message": "登录按钮无法点击"
            })

    else:
        return jsonify({
            "status": "false",
            "message": "请先在个人中心处配置豆丁文库账密或cookie"
        })
