from flask_login import UserMixin
from persistence.db import get_connection
from enums.role import Role
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin):
    """
    Representa a un usuario del sistema.
    Puede tener rol de administrador o jugador.
    """

    def __init__(self, id: int, name: str, email: str, password: str, role: str) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    
    def save(name: str, email: str, password: str, role: str) -> bool:
        """
        Guarda un usuario en la base de datos con contraseña hasheada.
        """

        try:
            connection = get_connection()
            cursor = connection.cursor()

            hash_password = generate_password_hash(password)

            sql = """
                INSERT INTO users(name, email, password, role)
                VALUES(%s, %s, %s, %s)
            """

            cursor.execute(sql, (name, email, hash_password, role))
            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Exception as ex:
            print(f"Error saving user: {ex}")
            return False

    
    def check_email_exists(email: str) -> bool:
        """
        Verifica si un correo ya está registrado.
        """

        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (email,))

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            return user is not None

        except Exception as ex:
            print(f"Error checking email: {ex}")
            return False

    
    def check_login(email: str, password: str):
        """
        Verifica credenciales del usuario.
        """

        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(user["password"], password):
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    user["role"]
                )

            return None

        except Exception as ex:
            print(f"Error checking login: {ex}")
            return None
        
    def get_by_id(user_id: int):
        """
        Busca un usuario por su id.
        """

        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user:
                return User(
                    user["id"],
                    user["name"],
                    user["email"],
                    user["password"],
                    user["role"]
                )

            return None

        except Exception as ex:
            print(f"Error getting user by id: {ex}")
            return None