import pymysql
import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', 3306)),  # Usa 3306 por defecto ya que tu MySQL está activo ahí
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'Pelus@123'),
        database=os.getenv('DB_NAME', 'juego_db'),
        cursorclass=pymysql.cursors.DictCursor
    )