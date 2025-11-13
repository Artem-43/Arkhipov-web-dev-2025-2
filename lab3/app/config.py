import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')