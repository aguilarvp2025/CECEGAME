import pymysql
from persistence.db import get_connection
from utils.crypto_utils import cifrar_palabra, descifrar_palabra
from typing import List, Dict, Any


class Level:
    """
    Representa un nivel del juego.
    Contiene la imagen del personaje, la pista y la palabra secreta cifrada.
    Aplica el Principio de Responsabilidad Única: solo gestiona datos de niveles.
    """

    def __init__(self, id: int, level_number: int, image: str, hint: str, secret_word: str) -> None:
        """
        Inicializa un objeto Level con sus atributos.

        Args:
            id (int): Identificador único del nivel en la base de datos.
            level_number (int): Número de orden del nivel en el juego.
            image (str): Ruta relativa a la imagen del personaje.
            hint (str): Pista que se muestra al jugador.
            secret_word (str): Palabra secreta cifrada con Fernet AES.
        """
        self.id = id
        self.level_number = level_number
        self.image = image
        self.hint = hint
        self.secret_word = secret_word

    @staticmethod
    def save(image: str, hint: str, secret_word: str, level_number: int) -> bool:
        """
        Guarda un nuevo nivel en la base de datos usando consultas parametrizadas.

        Args:
            image (str): Ruta relativa a la imagen del personaje.
            hint (str): Pista que se mostrará al jugador.
            secret_word (str): Palabra secreta ya cifrada con Fernet AES.
            level_number (int): Número de orden del nivel.

        Returns:
            bool: True si el nivel fue guardado exitosamente, False en caso de error.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Cifrar la palabra secreta antes de guardarla (AES via Fernet - Luis)
            secret_word_encrypted = cifrar_palabra(secret_word)

            sql = """
                INSERT INTO levels (image, hint, secret_word, level_number)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(sql, (image, hint, secret_word_encrypted, level_number))
            connection.commit()

            cursor.close()
            connection.close()

            return True

        except Exception as ex:
            print(f"Error saving level: {ex}")
            return False

    @staticmethod
    def validate_answer(level_id: int, user_answer: str) -> bool:
        """
        Valida si la respuesta del jugador coincide con la palabra secreta del nivel.
        Descifra la palabra almacenada antes de comparar (AES via Fernet - Luis).

        Args:
            level_id (int): ID del nivel en la base de datos.
            user_answer (str): Respuesta ingresada por el jugador.

        Returns:
            bool: True si la respuesta es correcta, False en caso contrario.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = "SELECT secret_word FROM levels WHERE id = %s"
            cursor.execute(sql, (level_id,))
            level = cursor.fetchone()

            cursor.close()
            connection.close()

            if not level:
                return False

            # Descifrar la palabra para comparar (AES via Fernet - Luis)
            secret_word = descifrar_palabra(level["secret_word"])

            return user_answer.lower().strip() == secret_word.lower().strip()

        except Exception as ex:
            print(f"Error validating answer: {ex}")
            return False

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """
        Obtiene todos los niveles de la base de datos ordenados por level_number ASC.
        El cursor retorna diccionarios (DictCursor) para que el motor del juego
        pueda acceder a los campos por nombre (n['level_number'], n['hint'], etc.).

        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos de cada nivel.
                                  Retorna lista vacía si ocurre un error.
        """
        try:
            connection = get_connection()
            cursor = connection.cursor()

            sql = "SELECT * FROM levels ORDER BY level_number ASC"
            cursor.execute(sql)

            niveles = cursor.fetchall()

            cursor.close()
            connection.close()

            return niveles

        except Exception as ex:
            print(f"Error getting levels: {ex}")
            return []
