import os
from getpass import getpass

from app import app
from extensions import db
from models import User


def print_users():
    print("\n📋 USUARIOS EN BD:")
    users = User.query.all()

    if not users:
        print("No hay usuarios.")
        return

    for u in users:
        print(f"- ID: {u.id} | Username: {u.username} | Role: {u.role}")


def create_user():
    print("=== CREAR USUARIO ===")

    username = input("Username: ").strip()

    if not username:
        print("❌ Username no válido")
        return

    password = getpass("Password: ")
    password2 = getpass("Confirmar password: ")

    if password != password2:
        print("❌ Las contraseñas no coinciden")
        return

    print("\nRoles disponibles: USER, EMPLEADO, ADMIN")
    role = input("Role: ").strip().upper()

    if role not in ["USER", "EMPLEADO", "ADMIN"]:
        print("❌ Role inválido, usando USER por defecto")
        role = "USER"

    with app.app_context():
        # comprobar duplicado
        if User.query.filter_by(username=username).first():
            print("❌ Ese usuario ya existe")
            return

        user = User(username=username, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print(f"\n✅ Usuario creado: {username} ({role})")


if __name__ == "__main__":
    with app.app_context():
        create_user()
        print_users()
