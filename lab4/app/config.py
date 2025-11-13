import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')