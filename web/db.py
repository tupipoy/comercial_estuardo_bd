import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Abre una conexión MySQL con los parámetros definidos en el entorno."""
    host = os.getenv("DB_HOST") or os.getenv("MYSQLHOST") or "localhost"
    port = os.getenv("DB_PORT") or os.getenv("MYSQLPORT") or "3306"
    user = os.getenv("DB_USER") or os.getenv("MYSQLUSER") or "root"
    password = os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD") or ""
    database = os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE") or "comercial_estuardo_db"
    return pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
