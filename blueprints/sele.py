import os

from flask import Blueprint, request, jsonify, g
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from sqlalchemy.exc import IntegrityError

from decorators import login_required
from models import UserInfoByBaidu, BaiduCookie, User
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from extension import db
import time


# 爬虫下载文库

bp = Blueprint("seleBaidu", __name__, url_prefix="/bd")


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


def loginBaidu():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 运行在无头模式
    chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)

    user_id = g.user.id
    userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)
    user: User = User.query.get(user_id)
    if userInfo:
        username = userInfo.username
        password = userInfo.password
        try:
            driver.get("https://wenku.baidu.com")
            print("请求网站成功")
            try:
                guanggao = driver.find_element(By.XPATH, '//*[@id="wk-chat"]/div[2]/div[8]/div[1]/div[1]')
                guanggao.click()
            except ElementNotInteractableException:
                pass
            except NoSuchElementException:
                pass

            loginButton = (By.CLASS_NAME, 'user-text')
            WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(loginButton))
            driver.find_element(By.CLASS_NAME, 'user-text').click()
            usernameInput = (By.ID, 'TANGRAM__PSP_11__userName')
            WebDriverWait(driver, 5).until(expected_conditions.presence_of_element_located(usernameInput))

            driver.find_element(By.ID, 'TANGRAM__PSP_11__userName').send_keys(username)
            driver.find_element(By.ID, 'TANGRAM__PSP_11__password').send_keys(password)
            driver.find_element(By.ID, 'TANGRAM__PSP_11__isAgree').click()
            driver.find_element(By.ID, 'TANGRAM__PSP_11__submit').send_keys(Keys.RETURN)
            time.sleep(1)
            goToVerify = driver.find_element(By.ID, 'goToVerify')
            if goToVerify:
                return jsonify({
                    "status": "false",
                    "message": "登录需要手机认证，请手动登录后复制cookie"
                })

            userIcon = driver.find_element(By.CLASS_NAME, 'user-icon')
            if userIcon:
                cookies = driver.get_cookies()

                # 转换cookie格式
                cookie_str = ""
                for cookie in cookies:
                    cookie_name = cookie['name']
                    cookie_value = cookie['value']
                    cookie_str += f"{cookie_name}={cookie_value}; "

                baiduCookie = BaiduCookie()
                baiduCookie.user = user
                baiduCookie.cookies = cookie_str
                try:
                    db.session.add(baiduCookie)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return jsonify({
                        "status": "false",
                        "message": "向表中添加cookie失败"
                    })
                driver.quit()
                return cookies

            else:
                return jsonify({
                    "status": "false",
                    "message": "用户名或密码错误，登录未成功"
                })

        except TimeoutException:
            return jsonify({
                "status": "false",
                "message": "百度文库网站或某一标签加载时间过长"
            })
        except ElementClickInterceptedException:
            return jsonify({
                "status": "false",
                "message": "登录按钮无法点击"
            })

        finally:
            driver.quit()

    else:
        return jsonify({
            "status": "false",
            "message": "请先在个人中心处配置百度文库账密或cookie"
        })


# 百度文库
@bp.route("/bdwk", methods=['POST', ])
@login_required
def downloadDocInBaidu():
    user_id = g.user.id
    user: User = User.query.get(user_id)
    # download_dir = r"C:\\"
    download_dir = user.downloadpath
    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless")  # 运行在无头模式
    # chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统

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

        baiduCookie: BaiduCookie = BaiduCookie.query.get(user_id)

        if baiduCookie:
            cookies = baiduCookie.cookies.split(";")
            for cookie in cookies:
                cookie = cookie.strip()
                cookie_name, cookie_value = cookie.split("=", maxsplit=1)
                driver.add_cookie({'name': cookie_name, 'value': cookie_value})

            driver.refresh()
            print("网站刷新成功")
            userIcon = driver.find_element(By.CLASS_NAME, 'user-icon')
            if not userIcon:
                response = loginBaidu()
                try:
                    responseData = response.get_json()
                    return responseData
                except Exception as e:
                    print(e)
                    for cookie in response:
                        driver.add_cookie(cookie)

                driver.refresh()

        else:
            response = loginBaidu()
            try:
                responseData = response.get_json()
                return responseData
            except Exception as e:
                print(e)
                for cookie in response:
                    driver.add_cookie(cookie)

            driver.refresh()

        try:
            guanggao = driver.find_element(By.XPATH, '//*[@id="app"]/div[3]/div/div[2]/div[2]/div[5]')
            guanggao.click()
        except ElementNotInteractableException:
            pass

        downloadButton = (By.XPATH, '//*[@id="app"]/div[2]/div[1]/div[2]/div[3]/div/div[1]/div/div[2]/div[2]')
        WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(downloadButton))

        try:
            driver.find_element(By.XPATH,
                                '//*[@id="app"]/div[2]/div[1]/div[2]/div[3]/div/div[1]/div/div[2]/div[2]').click()

            time.sleep(5)

            final_files = os.listdir(download_dir)
            new_files = set(final_files) - set(initial_files)

            # 获取网站源码

            page_source = driver.page_source

            if "联合会员" in page_source:
                driver.quit()
                return jsonify({
                    "status": "false",
                    "message": "该文档需要会员"
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

