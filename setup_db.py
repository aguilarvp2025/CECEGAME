import os
from werkzeug.security import generate_password_hash
from persistence.db import get_connection

# Intentar importar la función de cifrado de Luis Campa
try:
    from utils.crypto_utils import cifrar_palabra
except ImportError:
    def cifrar_palabra(palabra: str) -> str:
        return palabra

def setup_database():
    print("Conectándose a la base de datos a través de persistence.db...")
    try:
        # Reutilizamos la conexión única del proyecto
        connection = get_connection()
        cursor = connection.cursor()
        print("¡Conexión establecida con éxito!")
        
        # 1. Crear tabla de usuarios
        print("Creando tabla 'users'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL
            );
        """)
        
        # 2. Crear tabla de niveles
        print("Creando tabla 'levels'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                id INT AUTO_INCREMENT PRIMARY KEY,
                image VARCHAR(255) NOT NULL,
                hint TEXT NOT NULL,
                secret_word VARCHAR(255) NOT NULL,
                level_number INT NOT NULL UNIQUE
            );
        """)
        
        # 3. Crear administrador por defecto si no existe
        cursor.execute("SELECT id FROM users WHERE email = %s", ("admin@juego.com",))
        if not cursor.fetchone():
            print("Insertando usuario administrador de prueba (admin@juego.com / admin123)...")
            hash_pass = generate_password_hash("admin123")
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                ("Administrador Sheriff", "admin@juego.com", hash_pass, "ADMINISTRADOR")
            )
            
        # 4. Insertar niveles iniciales de prueba cifrados si la tabla está vacía
        cursor.execute("SELECT id FROM levels LIMIT 1")
        if not cursor.fetchone():
            print("Insertando niveles iniciales con palabras cifradas...")
            # Nivel 1
            palabra_1_cifrada = cifrar_palabra("pepe")
            cursor.execute(
                "INSERT INTO levels (image, hint, secret_word, level_number) VALUES (%s, %s, %s, %s)",
                ("pepelviejo.jpg", "Un viejo sabio del oeste de nombre gracioso.", palabra_1_cifrada, 1)
            )
            # Nivel 2
            palabra_2_cifrada = cifrar_palabra("outlaw")
            cursor.execute(
                "INSERT INTO levels (image, hint, secret_word, level_number) VALUES (%s, %s, %s, %s)",
                ("TheOutlaw_gamer.jpg", "La palabra en inglés para referirse a un forajido.", palabra_2_cifrada, 2)
            )
            
        connection.commit()
        cursor.close()
        connection.close()
        print("\n¡Base de datos local configurada y poblada con éxito total! 🚀🤠")
        
    except Exception as ex:
        print(f"\nError al configurar la base de datos: {ex}")
        print("Asegúrate de que tus credenciales en persistence/db.py (o archivo .env) sean correctas y que tu servidor local de MySQL esté encendido.")

if __name__ == "__main__":
    setup_database()
