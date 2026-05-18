from enum import Enum

 ## Define los roles disponibles para los usuarios del sistema.
   
class Role(Enum):
    ADMIN = "admin"
    PLAYER = "player"