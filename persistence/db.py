import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3307,
        user='root',
        password='admin',
        database='juego_db',
        cursorclass=pymysql.cursors.DictCursor
    )