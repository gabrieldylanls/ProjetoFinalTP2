"""População idempotente do banco usado na demonstração local."""

import sqlite3
from pathlib import Path

from app.application.product_service import ProductService
from app.application.user_service import UserService
from app.infrastructure.product_repository import SQLiteProductRepository
from app.infrastructure.user_repository import SQLiteUserRepository

DEMO_USERS = (
    {
        "name": "Administrador",
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin",
    },
    {
        "name": "Usuário Demonstração",
        "email": "usuario@example.com",
        "password": "usuario123",
        "role": "user",
    },
)

DEMO_PRODUCTS = (
    ("Arroz Integral", "Tio João", 12.50, "7891000000001", 30),
    ("Feijão Carioca", "Camil", 8.90, "7891000000002", 25),
    ("Macarrão Espaguete", "Renata", 6.75, "7891000000003", 40),
    ("Açúcar Refinado", "União", 5.60, "7891000000004", 18),
    ("Café Torrado", "Pilão", 18.90, "7891000000005", 22),
    ("Leite Integral", "Itambé", 5.25, "7891000000006", 36),
    ("Óleo de Soja", "Liza", 7.80, "7891000000007", 20),
    ("Farinha de Trigo", "Dona Benta", 6.40, "7891000000008", 15),
    ("Biscoito Cream Cracker", "Vitarella", 4.85, "7891000000009", 28),
    ("Molho de Tomate", "Quero", 3.75, "7891000000010", 32),
    ("Sabão em Pó", "Omo", 16.90, "7891000000011", 12),
    ("Papel Higiênico", "Neve", 14.50, "7891000000012", 16),
)


def seed_demo_data(connection: sqlite3.Connection) -> dict[str, int]:
    """DEMO: cria usuários e produtos fictícios ausentes.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna quantos usuários e produtos foram criados.
    """
    product_repository = SQLiteProductRepository(connection)
    product_repository.create_table()
    user_repository = SQLiteUserRepository(connection)
    user_repository.create_table()
    product_service = ProductService(product_repository)
    user_service = UserService(user_repository)

    users_created = _seed_users(user_service, user_repository)
    products_created = _seed_products(product_service, product_repository)
    return {
        "users_created": users_created,
        "products_created": products_created,
    }


def seed_demo_database(database_path: str | Path = "shopping.db") -> dict[str, int]:
    """DEMO: popula um arquivo SQLite para execução local.

    Pré-condição: database_path deve apontar para um arquivo acessível.
    Pós-condição: fecha a conexão e retorna o resumo da população.
    """
    connection = sqlite3.connect(database_path)
    try:
        return seed_demo_data(connection)
    finally:
        connection.close()


def _seed_users(user_service, user_repository) -> int:
    """DEMO: cria somente os usuários de demonstração ausentes."""
    created = 0
    for user_data in DEMO_USERS:
        if user_repository.get_user_by_email(user_data["email"]) is None:
            user_service.create_user(**user_data)
            created += 1
    return created


def _seed_products(product_service, product_repository) -> int:
    """DEMO: cria somente os produtos fictícios ausentes."""
    created = 0
    for name, brand, price, bar_code, quantity in DEMO_PRODUCTS:
        if product_repository.get_product_by_bar_code(bar_code) is None:
            product_service.create_product(
                name=name,
                brand=brand,
                price=price,
                bar_code=bar_code,
                quantity=quantity,
            )
            created += 1
    return created


if __name__ == "__main__":
    result = seed_demo_database()
    print(
        "Dados de demonstração prontos: "
        f"{result['users_created']} usuários e "
        f"{result['products_created']} produtos criados."
    )
