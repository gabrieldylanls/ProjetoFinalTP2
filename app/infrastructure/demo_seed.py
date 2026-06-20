"""População idempotente do banco usado na demonstração local."""

import sqlite3
from pathlib import Path

from app.application.store_service import StoreService
from app.application.user_service import UserService
from app.domain.product import Product
from app.infrastructure.product_repository import SQLiteProductRepository
from app.infrastructure.store_repository import SQLiteStoreRepository
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

DEMO_STORES = (
    ("Mercado Central", "Rua Principal, 100", "Aberto todos os dias"),
    ("Supermercado Econômico", "Avenida Brasil, 450", "Estacionamento gratuito"),
    ("Atacadão Popular", "Rodovia Norte, 1200", "Vendas em atacado e varejo"),
    ("Empório da Praça", "Praça das Flores, 25", "Produtos artesanais"),
    ("Mercado do Bairro", "Rua das Acácias, 78", None),
    ("Hipermercado Avenida", "Avenida Central, 980", "Funcionamento 24 horas"),
)

GENERATED_PRODUCT_COUNT = 3000
GENERATED_NAMES = (
    "Arroz",
    "Feijão",
    "Macarrão",
    "Café",
    "Leite",
    "Biscoito",
    "Farinha",
    "Açúcar",
    "Molho",
    "Sabonete",
    "Detergente",
    "Papel Toalha",
)
GENERATED_BRANDS = (
    "Boa Compra",
    "Casa Feliz",
    "Sabor Real",
    "Dia a Dia",
    "Nossa Marca",
    "Seleção",
)


def seed_demo_data(connection: sqlite3.Connection) -> dict[str, int]:
    """DEMO: cria usuários, locais e milhares de produtos ausentes.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna as quantidades criadas em cada catálogo.
    """
    product_repository = SQLiteProductRepository(connection)
    product_repository.create_table()
    user_repository = SQLiteUserRepository(connection)
    user_repository.create_table()
    store_repository = SQLiteStoreRepository(connection)
    store_repository.create_table()
    user_service = UserService(user_repository)
    store_service = StoreService(store_repository)

    users_created = _seed_users(user_service, user_repository)
    stores_created = _seed_stores(store_service, store_repository)
    products_created = _seed_products(product_repository)
    return {
        "users_created": users_created,
        "stores_created": stores_created,
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


def _seed_stores(store_service, store_repository) -> int:
    """DEMO: cria somente os locais de compra ausentes."""
    existing = {
        (store.name.casefold(), store.address.casefold())
        for store in store_repository.list_stores()
    }
    created = 0
    for name, address, observation in DEMO_STORES:
        key = (name.casefold(), address.casefold())
        if key not in existing:
            store_service.create_store(
                name=name,
                address=address,
                observation=observation,
            )
            created += 1
    return created


def _seed_products(product_repository) -> int:
    """DEMO: cria produtos validados em lote e sem duplicação."""
    existing_bar_codes = product_repository.list_bar_codes()
    missing_products = []
    for name, brand, price, bar_code, quantity in _demo_product_rows():
        if bar_code not in existing_bar_codes:
            missing_products.append(
                (
                    Product(
                        name=name,
                        brand=brand,
                        price=price,
                        bar_code=bar_code,
                    ),
                    quantity,
                )
            )
    product_repository.add_products(missing_products)
    return len(missing_products)


def _demo_product_rows():
    """DEMO: produz dados determinísticos para o catálogo fictício."""
    yield from DEMO_PRODUCTS
    for index in range(1, GENERATED_PRODUCT_COUNT + 1):
        name = GENERATED_NAMES[(index - 1) % len(GENERATED_NAMES)]
        brand = GENERATED_BRANDS[(index - 1) % len(GENERATED_BRANDS)]
        price = round(2.50 + ((index * 137) % 2500) / 100, 2)
        bar_code = f"790{index:010d}"
        quantity = (index * 7) % 120
        yield (
            f"{name} Fictício {index:04d}",
            brand,
            price,
            bar_code,
            quantity,
        )


if __name__ == "__main__":
    result = seed_demo_database()
    print(
        "Dados de demonstração prontos: "
        f"{result['users_created']} usuários e "
        f"{result['stores_created']} locais e "
        f"{result['products_created']} produtos criados."
    )
