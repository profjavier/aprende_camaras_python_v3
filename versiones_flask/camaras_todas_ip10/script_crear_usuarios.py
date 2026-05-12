from app import app
from extensions import db
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

# Muestra los usuarios
def print_users():
    print(f"\n{CYAN}USUARIOS EN BD:{RESET}")

    users = User.query.all()

    # si no hay usuarios
    if not users:
        print(f"{YELLOW}No hay usuarios.{RESET}")
        return

    # imprime los usuarios
    for u in users:
        print(
            f"{BLUE}- ID: {u.id}{RESET} | "
            f"{GREEN}Username: {u.username}{RESET} | "
            f"{YELLOW}Role: {u.role}{RESET}"
        )

# Crear un USUARIO
def create_user():

    print(f"{CYAN}***** CREAR USUARIO *****{RESET}")

    # pedir datos al usuario
    username = input(f"{BLUE}Username: {RESET}").strip()
    password = input(f"{BLUE}Password: {RESET}").strip()

    print(f"\n{YELLOW}Roles disponibles: USER, ADMIN{RESET}")
    role = input(f"{BLUE}Rol (user, ADMIN): {RESET}").strip().upper()
    if role != "USER":
        role = "ADMIN"

    with app.app_context():

        # comprobar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            print(f"{RED}Ese usuario ya existe{RESET}")
            return

        # crear objeto usuario
        user = User(username=username, role=role)

        # encriptar contraseña
        user.set_password(password)

        # guardar en base de datos
        db.session.add(user)
        db.session.commit()

        print(f"{GREEN}\nUsuario creado: {username} ({role}){RESET}")


# Programa principal
if __name__ == "__main__":

    with app.app_context():

        create_user()
        print_users()