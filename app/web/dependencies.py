"""Composição das dependências utilizadas pela camada web."""

import sqlite3

from app.application.cart_service import CartService
from app.application.product_service import ProductService
from app.application.shopping_list_service import ShoppingListService
from app.application.store_service import StoreService
from app.application.user_service import UserService
from app.infrastructure.product_repository import SQLiteProductRepository
from app.infrastructure.shopping_list_repository import (
    SQLiteShoppingListRepository,
)
from app.infrastructure.store_repository import SQLiteStoreRepository
from app.infrastructure.user_repository import SQLiteUserRepository


def initialize_product_service(
    connection: sqlite3.Connection,
) -> ProductService:
    """AD01/US02/AD02/AD03: inicializa as dependências de produtos.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna o serviço com tabela e repositório configurados.
    """
    product_repository = SQLiteProductRepository(connection)
    product_repository.create_table()
    return ProductService(product_repository)


def initialize_cart_service(
    product_service: ProductService,
) -> CartService:
    """US04: inicializa o carrinho reutilizando o serviço de produtos.

    Pré-condição: product_service deve permitir consulta de produtos.
    Pós-condição: retorna o serviço de carrinho configurado.
    """
    return CartService(product_service)


def initialize_user_service(
    connection: sqlite3.Connection,
) -> UserService:
    """US01: inicializa as dependências de autenticação.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna o serviço com tabela e repositório configurados.
    """
    user_repository = SQLiteUserRepository(connection)
    user_repository.create_table()
    return UserService(user_repository)


def initialize_shopping_list_service(
    connection: sqlite3.Connection,
) -> ShoppingListService:
    """US03: inicializa as dependências de listas de compras.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna o serviço com tabela e repositório configurados.
    """
    repository = SQLiteShoppingListRepository(connection)
    repository.create_table()
    product_repository = SQLiteProductRepository(connection)
    product_repository.create_table()
    return ShoppingListService(
        repository,
        product_repository=product_repository,
    )


def initialize_store_service(
    connection: sqlite3.Connection,
) -> StoreService:
    """US06: inicializa as dependências de locais de compra.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna o serviço com tabela e repositório configurados.
    """
    repository = SQLiteStoreRepository(connection)
    repository.create_table()
    return StoreService(repository)
