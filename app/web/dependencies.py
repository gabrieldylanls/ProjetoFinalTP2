"""Composição das dependências utilizadas pela camada web."""

import sqlite3

from app.application.product_service import ProductService
from app.infrastructure.product_repository import SQLiteProductRepository


def initialize_product_service(
    connection: sqlite3.Connection,
) -> ProductService:
    """AD01: inicializa as dependências do cadastro de produtos.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna o serviço com tabela e repositório configurados.
    """
    product_repository = SQLiteProductRepository(connection)
    product_repository.create_table()
    return ProductService(product_repository)
