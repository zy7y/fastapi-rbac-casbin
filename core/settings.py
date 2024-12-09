# JWT
import os.path

SECRET_KEY = "lLNiBWPGiEmCLLR9kRGidgLY7Ac1rpSWwfGzTJpTmCU"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# ORN
DB_URL = "sqlite://db.sqlite3"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# 上传文件保留路径
DISK_PATH = os.path.join(BASE_DIR, "disk")
