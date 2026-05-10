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


if __name__ == "__main__":
    with app.app_context():
        print_users()
