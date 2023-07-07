import os

"""Bot Data"""
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_NOTIFICATIONS_BOT_TOKEN = os.getenv("TELEGRAM_NOTIFICATIONS_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

"""DataBase Data"""
PSQL_DB_NAME = os.getenv("PSQL_DB_NAME", "")
PSQL_DB_USER = os.getenv("PSQL_DB_USER", "")
PSQL_DB_PASSWORD = os.getenv("PSQL_DB_PASSWORD", "")
PSQL_DB_HOST = os.getenv("PSQL_DB_HOST", "")

"""Payment Data (YaKassa)"""
ACCOUNT_ID = os.getenv("ACCOUNT_ID", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")
