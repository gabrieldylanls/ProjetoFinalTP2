"""Persistência SQLite do histórico de preços observados."""

import sqlite3
from datetime import datetime

from app.domain.product import Product
from app.domain.product_price import ProductPrice


class SQLiteProductPriceRepository:
    """US06: armazena preços observados sem alterar o preço base."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """US06: inicializa o repositório de preços.

        Pré-condição: connection deve ser uma conexão SQLite aberta.
        Pós-condição: o repositório utiliza a conexão recebida.
        """
        self.connection = connection

    def create_table(self) -> None:
        """US06: cria a tabela independente de histórico de preços.

        Pré-condição: a conexão deve estar aberta.
        Pós-condição: a tabela product_prices existe.
        """
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS product_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_bar_code TEXT NOT NULL,
                store_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                price REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_product_prices_product
            ON product_prices (product_bar_code, created_at);
            """
        )
        self.connection.commit()

    def add_price(self, product_price: ProductPrice) -> None:
        """US06: adiciona uma observação ao histórico.

        Pré-condição: product_price deve conter dados validados.
        Pós-condição: um novo registro é persistido sem substituir anteriores.
        """
        self.connection.execute(
            """
            INSERT INTO product_prices (
                product_bar_code,
                store_id,
                user_id,
                price,
                created_at
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                product_price.product_bar_code,
                product_price.store_id,
                product_price.user_id,
                product_price.price,
                product_price.created_at.isoformat(),
            ),
        )
        self.connection.commit()

    def list_prices_by_product(
        self,
        product_bar_code: str,
    ) -> list[ProductPrice]:
        """US06: lista o histórico de um produto.

        Pré-condição: product_bar_code identifica o produto consultado.
        Pós-condição: retorna registros do mais recente para o mais antigo.
        """
        rows = self.connection.execute(
            """
            SELECT product_bar_code, store_id, user_id, price, created_at
            FROM product_prices
            WHERE product_bar_code = ?
            ORDER BY created_at DESC, id DESC;
            """,
            (product_bar_code,),
        ).fetchall()
        return [
            ProductPrice(
                product_bar_code=row[0],
                store_id=row[1],
                user_id=row[2],
                price=row[3],
                created_at=datetime.fromisoformat(row[4]),
            )
            for row in rows
        ]

    def list_price_keys(self) -> set[tuple[str, int]]:
        """DEMO: retorna vínculos produto/local já registrados."""
        rows = self.connection.execute(
            "SELECT product_bar_code, store_id FROM product_prices;"
        ).fetchall()
        return {(row[0], row[1]) for row in rows}

    def add_prices(self, product_prices: list[ProductPrice]) -> None:
        """DEMO: persiste vários preços observados em uma transação."""
        self.connection.executemany(
            """
            INSERT INTO product_prices (
                product_bar_code, store_id, user_id, price, created_at
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            [
                (
                    item.product_bar_code,
                    item.store_id,
                    item.user_id,
                    item.price,
                    item.created_at.isoformat(),
                )
                for item in product_prices
            ],
        )
        self.connection.commit()

    def list_products_by_store(
        self,
        store_id: int,
        query: str,
        limit: int,
        offset: int,
    ) -> list[tuple[Product, int, float]]:
        """US06/WEB: lista produtos com último preço observado na loja."""
        pattern = f"%{query}%"
        rows = self.connection.execute(
            """
            SELECT p.bar_code, p.name, p.brand, p.price, p.quantity, pp.price
            FROM products AS p
            JOIN product_prices AS pp
              ON pp.product_bar_code = p.bar_code
            WHERE p.active = 1
              AND pp.store_id = ?
              AND pp.id = (
                  SELECT MAX(latest.id)
                  FROM product_prices AS latest
                  WHERE latest.product_bar_code = pp.product_bar_code
                    AND latest.store_id = pp.store_id
              )
              AND (
                  ? = ''
                  OR p.name LIKE ? COLLATE NOCASE
                  OR p.brand LIKE ? COLLATE NOCASE
              )
            ORDER BY p.name COLLATE NOCASE, p.bar_code
            LIMIT ? OFFSET ?;
            """,
            (store_id, query, pattern, pattern, limit, offset),
        ).fetchall()
        return [
            (
                Product(
                    bar_code=row[0],
                    name=row[1],
                    brand=row[2],
                    price=row[3],
                ),
                row[4],
                row[5],
            )
            for row in rows
        ]

    def count_products_by_store(self, store_id: int, query: str) -> int:
        """US06/WEB: conta produtos associados à loja e busca."""
        pattern = f"%{query}%"
        return self.connection.execute(
            """
            SELECT COUNT(DISTINCT p.bar_code)
            FROM products AS p
            JOIN product_prices AS pp
              ON pp.product_bar_code = p.bar_code
            WHERE p.active = 1
              AND pp.store_id = ?
              AND (
                  ? = ''
                  OR p.name LIKE ? COLLATE NOCASE
                  OR p.brand LIKE ? COLLATE NOCASE
              );
            """,
            (store_id, query, pattern, pattern),
        ).fetchone()[0]

    def find_lowest_price_by_product(self, product_bar_code: str) -> tuple | None:
        """US07: retorna o menor preço observado para um produto.

        Pré-condição: product_bar_code deve identificar o produto consultado.
        Pós-condição: retorna preço, local e data ou None quando não houver dado.
        """
        return self.connection.execute(
            """
            SELECT pp.price, pp.created_at, s.id, s.name
            FROM product_prices AS pp
            JOIN stores AS s ON s.id = pp.store_id
            WHERE pp.product_bar_code = ?
            ORDER BY pp.price ASC, pp.created_at DESC, pp.id DESC
            LIMIT 1;
            """,
            (product_bar_code,),
        ).fetchone()
