import os
import threading
from urllib.parse import quote

from flask import Blueprint, request, jsonify, g
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from sqlalchemy.exc import IntegrityError

from decorators import login_required
from models import UserInfoByBaidu, User
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, \
    ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from extension import db
import time

# 爬虫下载文库

bp = Blueprint("seleBaidu", __name__, url_prefix="/bd")


def start_browser():
    service = ChromeService(ChromeDriverManager().install())
    options = Options()
    options.add_experimental_option("prefs", {
        "page.load.strategy": "eager"
    })
    # chrome_options.add_argument("--disable-images")  # 禁止图片加载
    # 要让js配合翻页，不能禁止js
    # chrome_options.add_argument("--disable-javascript")  # 禁止js
    # chrome_options.add_argument("--headless")  # 运行在无头模式
    # chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver = webdriver.Chrome(options=options, service=service)
    return driver


@bp.route("/search", methods=['GET', ])
def runInThread():
    driver = start_browser()
    for idx in range(5):
        threading.Thread(target=getDataByBaidu, args=(driver, idx)).start()

    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            thread.join()


# @bp.route("/search", methods=['GET', ])
# # @login_required
def getDataByBaidu(driver: webdriver.Chrome, idx: int):
    driver.set_page_load_timeout(5)
    print("配置驱动完成")
    lock = threading.Lock()
    searchDoc = request.args.get("searchDoc")
    searchDoc_encode = quote(searchDoc)
    path = f'https://wenku.baidu.com/search?word={searchDoc_encode}&pn='
    url_list = [path + str(page) for page in range(1, 6)]
    print(url_list)
    print("请求getDate")

    docsData = []
    try:
        lock.acquire()

        driver.execute_script(f"window.open('{url_list[idx]}')")
        driver.switch_to.window(driver.window_handles[idx + 1])
        print("请求网站成功")
        time.sleep(0.5)
        driver.refresh()

        docs = driver.find_elements(By.CSS_SELECTOR, '.list-item.doc-item-tile.layout-column')

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

        print("爬取完成")
        # print(docsData[0][1])
        driver.quit()
        return jsonify({
            "status": "success",
            "message": "请求成功",
            "docsData": docsData
        }), True

    except TimeoutException:
        return jsonify({
            "status": "false",
            "message": "访问网站超时"
        }), False

    finally:
        lock.release()


@bp.route("/loginbd", methods=['POST', ])
def loginBaidu():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 运行在无头模式
    chrome_options.add_argument("--disable-images")  # 禁止图片加载
    chrome_options.add_argument("--disable-gpu")  # 适用于Windows系统
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(10)
    print("配置驱动完成")
    "goToVerify"
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
            time.sleep(100)
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

    try:
        docPath = request.get_json().get("docPath")
        if not docPath:
            return jsonify({
                "status": "false",
                "message": "文档地址为空"
            })

    except Exception:
        return jsonify({
            "status": "false",
            "message": "接收文档地址错误"
        })

    try:
        initial_files = os.listdir(download_dir)

        driver.get(docPath)
        print("请求网站成功")
        # time.sleep(1)

        userInfo: UserInfoByBaidu = UserInfoByBaidu.query.get(user_id)

        if userInfo.cookies:
            cookies = userInfo.cookies.split(";")
            # 将字符串转换为字典格式
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

            try:
                driver.find_element(By.CSS_SELECTOR, '.btn-download.btn-1.btn-.had-doc').click()
                # downloadButton2 = (By.CSS_SELECTOR, '.btn-download.btn-1.btn-.had-doc')
                # WebDriverWait(driver, 5).until(expected_conditions.element_to_be_clickable(downloadButton2))
            except ElementClickInterceptedException:
                pass
            except ElementNotInteractableException:
                pass

            time.sleep(3)

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
                        "status": "success",
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
