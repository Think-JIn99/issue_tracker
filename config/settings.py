# settings.py
from dotenv import load_dotenv
import os
from pathlib import Path

# 현재 스크립트 파일의 경로를 가져옴
cwd = Path().cwd()

load_dotenv(str(cwd.joinpath("config/.env")))
# load_dotenv("/Users/jin/Programming/project/issue_tracker/config/.env")
app_env = os.getenv("APP_ENV", "dev")

USER_ID = os.getenv("LOCAL_ID")
PASSWORD = os.getenv("LOCAL_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
HOST = os.getenv("LOCAL_HOST")

DB_ENDPOINT = f"mysql+pymysql://{USER_ID}:{PASSWORD}@{HOST}/{DB_NAME}"
