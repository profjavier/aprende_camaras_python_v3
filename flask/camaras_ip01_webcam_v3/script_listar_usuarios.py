# script_listar_usuarios.py

from app import app
from models import User

# COLORES Y ESTILOS ANSI PARA CONSOLA
# Colores
RED = "\033[91m"       # ROJO
GREEN = "\033[92m"     # VERDE
YELLOW = "\033[93m"    # AMARILLO
BLUE = "\033[94m"      # AZUL
CYAN = "\033[96m"      # CYAN
# estilos
UNDERLINE = "\033[4m"
BOLD = "\033[1m"

# resetear color/estilo
RESET = "\033[0m"      # RESET


# Mostrar los usuarios
def print_users():
    # Título principal
    print(
        f"\n{BOLD}{UNDERLINE}{CYAN}"
        f"USUARIOS EN BASE DE DATOS"
        f"{RESET}"
    )

    # Obtener todos los usuarios
    users = User.query.all()

    # Comprobar si existen usuarios
    if not users:
        print( f"{YELLOW}No hay usuarios registrados.{RESET}" )
        return

    # Mostrar usuarios
    for u in users:
        print(
            f"{BLUE}ID:{RESET} {u.id} | "
            f"{GREEN}Username:{RESET} {u.username} | "
            f"{YELLOW}Role:{RESET} {u.role}"
        )

# Programa principal
if __name__ == "__main__":

    # crear contexto Flask
    with app.app_context():
        print_users()