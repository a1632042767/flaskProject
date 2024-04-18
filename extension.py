from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

db = SQLAlchemy()

# cors = CORS(resources={r'/*': {'origins': '*'}}, support_credentials=True)
cors = CORS(origins=['http://127.0.0.1:5500'], supports_credentials=True)
mail = Mail()