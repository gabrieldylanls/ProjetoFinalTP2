"""Composição das dependências utilizadas pela camada web."""

import sqlite3

from app.application.admin_metrics_service import AdminMetricsService
from app.application.cart_service import CartService
from app.application.pending_purchase_service import PendingPurchaseService
from app.application.product_price_service import ProductPriceService
from app.application.product_service import ProductService
from app.application.product_suggestion_service import ProductSuggestionService
from app.application.shopping_list_service import ShoppingListService
from app.application.store_service import StoreService
from app.application.user_service import UserService
from app.infrastructure.admin_metrics_repository import (
    SQLiteAdminMetricsRepository,
)
from app.infrastructure.pending_purchase_repository import (
    SQLitePendingPurchaseRepository,
)
from app.infrastructure.product_price_repository import (
    SQLiteProductPriceRepository,
)
from app.infrastructure.product_repository import SQLiteProductRepository
from app.infrastructure.product_suggestion_repository import (
    SQLiteProductSuggestionRepository,
)
from app.infrastructure.shopping_list_repository import (
    SQLiteShoppingListRepository,
)
from app.infrastructure.store_repository import SQLiteStoreRepository
from app.infrastructure.user_repository import SQLiteUserRepository


def initialize_admin_metrics_service(
    connection: sqlite3.Connection,
) -> AdminMetricsService:
    """AD04: inicializa a consulta de métricas administrativas.

    Pré-condição: as tabelas da aplicação devem estar inicializadas.
    Pós-condição: retorna o serviço conectado ao SQLite recebido.
    """
    repository = SQLiteAdminMetricsRepository(connection)
    return AdminMetricsService(repository)


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


def initialize_product_price_service(
    connection: sqlite3.Connection,
    product_service: ProductService,
    store_service: StoreService,
) -> ProductPriceService:
    """US06: inicializa as dependências do histórico de preços.

    Pré-condição: conexão e serviços de produto e local estão configurados.
    Pós-condição: retorna o serviço de preços com sua tabela criada.
    """
    price_repository = SQLiteProductPriceRepository(connection)
    price_repository.create_table()
    return ProductPriceService(
        price_repository=price_repository,
        product_repository=product_service.product_repository,
        store_repository=store_service.store_repository,
    )


def initialize_pending_purchase_service(
    connection: sqlite3.Connection,
) -> PendingPurchaseService:
    """US07: inicializa as dependências de itens pendentes."""
    pending_repository = SQLitePendingPurchaseRepository(connection)
    pending_repository.create_table()
    shopping_list_repository = SQLiteShoppingListRepository(connection)
    shopping_list_repository.create_table()
    product_repository = SQLiteProductRepository(connection)
    product_repository.create_table()
    price_repository = SQLiteProductPriceRepository(connection)
    price_repository.create_table()
    return PendingPurchaseService(
        pending_repository=pending_repository,
        shopping_list_repository=shopping_list_repository,
        product_repository=product_repository,
        price_repository=price_repository,
    )


def initialize_product_suggestion_service(
    connection: sqlite3.Connection,
    product_service: ProductService,
) -> ProductSuggestionService:
    """AD05: inicializa as dependências de sugestões de produtos."""
    suggestion_repository = SQLiteProductSuggestionRepository(connection)
    suggestion_repository.create_table()
    return ProductSuggestionService(
        suggestion_repository=suggestion_repository,
        product_service=product_service,
        product_repository=product_service.product_repository,
    )
