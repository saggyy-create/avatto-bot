import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID", "-100000000000")  # Telegram group ID for admin notifications
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://yourdomain.com/miniapp")  # URL of your Mini App
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))  # Admin Telegram IDs
DATABASE_PATH = os.getenv("DATABASE_PATH", "catalog_bot.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
