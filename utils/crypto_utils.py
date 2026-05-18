from cryptography.fernet import Fernet

# Llave secreta
KEY = b"OwDQOfk8bQQcXNE7Ior2grbF-U1RV2wS0u-ZMP9sdq4="


# Objeto para cifrar y descifrar
fernet = Fernet(KEY)


# Función para cifrar
def cifrar_palabra(palabra: str) -> str:
    return fernet.encrypt(palabra.encode()).decode()


# Función para descifrar
def descifrar_palabra(palabra_cifrada: str) -> str:
    return fernet.decrypt(palabra_cifrada.encode()).decode()
