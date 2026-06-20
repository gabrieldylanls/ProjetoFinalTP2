"""Persistência SQLite de produtos."""

import sqlite3

from app.domain.exceptions import DuplicateBarcodeError
from app.domain.product import Product
from app.domain.quantity import validate_quantity


class SQLiteProductRepository:
    """Armazena e consulta produtos em uma conexão SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Inicializa o repositório.

        Pré-condição: connection deve ser uma conexão SQLite aberta.
        Pós-condição: o repositório passa a utilizar a conexão recebida.
        """
        self.connection = connection

    def create_table(self) -> None:
        """Cria a tabela de produtos quando necessário.

        Pré-condição: a conexão deve estar aberta.
        Pós-condição: a tabela existe e a transação é confirmada.
        """
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                bar_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        self._ensure_active_column()
        self.connection.commit()

    def add_product(self, product: Product, quantity: int) -> None:
        """Persiste um produto e sua quantidade.

        Pré-condição: produto e quantidade válidos, com código ainda livre.
        Pós-condição: o registro é salvo ou uma exceção é lançada.
        """
        validate_quantity(quantity)

        if self.get_product_by_bar_code(product.bar_code) is not None:
            raise DuplicateBarcodeError(
                f"Já existe um produto com o código de barras {product.bar_code}."
            )

        self.connection.execute(
            """
            INSERT INTO products (bar_code, name, brand, price, quantity)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                product.bar_code,
                product.name,
                product.brand,
                product.price,
                quantity,
            ),
        )
        self.connection.commit()

    def get_product_by_bar_code(
        self,
        bar_code: str,
    ) -> tuple[Product, int] | None:
        """Busca um produto pelo código de barras.

        Pré-condição: bar_code deve identificar o registro procurado.
        Pós-condição: retorna produto e quantidade, ou None quando ausente.
        """
        row = self.connection.execute(
            """
            SELECT bar_code, name, brand, price, quantity
            FROM products
            WHERE bar_code = ?;
            """,
            (bar_code,),
        ).fetchone()

        if row is None:
            return None

        return self._to_product_with_quantity(row)

    def search_products_by_text(
        self,
        query: str,
    ) -> list[tuple[Product, int]]:
        """US02: busca produtos por parte do nome ou da marca.

        Pré-condição: query deve conter um texto não vazio.
        Pós-condição: retorna produtos compatíveis ou lista vazia.
        """
        search_pattern = f"%{query}%"
        rows = self.connection.execute(
            """
            SELECT bar_code, name, brand, price, quantity
            FROM products
            WHERE active = 1
              AND (
                  name LIKE ? COLLATE NOCASE
                  OR brand LIKE ? COLLATE NOCASE
              )
            ORDER BY name, bar_code;
            """,
            (search_pattern, search_pattern),
        ).fetchall()

        return [self._to_product_with_quantity(row) for row in rows]

    def list_active_products(self) -> list[tuple[Product, int]]:
        """WEB: lista todos os produtos ativos do catálogo.

        Pré-condição: a tabela products deve existir.
        Pós-condição: retorna produtos ativos ordenados por nome e código.
        """
        rows = self.connection.execute(
            """
            SELECT bar_code, name, brand, price, quantity
            FROM products
            WHERE active = 1
            ORDER BY name COLLATE NOCASE, bar_code;
            """
        ).fetchall()
        return [self._to_product_with_quantity(row) for row in rows]

    def list_active_products_page(
        self,
        query: str,
        limit: int,
        offset: int,
    ) -> list[tuple[Product, int]]:
        """WEB: lista uma página de produtos ativos.

        Pré-condição: limit e offset devem representar uma página válida.
        Pós-condição: retorna apenas os produtos da página solicitada.
        """
        search_pattern = f"%{query}%"
        rows = self.connection.execute(
            """
            SELECT bar_code, name, brand, price, quantity
            FROM products
            WHERE active = 1
              AND (
                  ? = ''
                  OR name LIKE ? COLLATE NOCASE
                  OR brand LIKE ? COLLATE NOCASE
              )
            ORDER BY name COLLATE NOCASE, bar_code
            LIMIT ? OFFSET ?;
            """,
            (query, search_pattern, search_pattern, limit, offset),
        ).fetchall()
        return [self._to_product_with_quantity(row) for row in rows]

    def count_active_products(self, query: str = "") -> int:
        """WEB: conta produtos ativos compatíveis com a busca.

        Pré-condição: query deve ser uma string, possivelmente vazia.
        Pós-condição: retorna a quantidade de registros compatíveis.
        """
        search_pattern = f"%{query}%"
        return self.connection.execute(
            """
            SELECT COUNT(*)
            FROM products
            WHERE active = 1
              AND (
                  ? = ''
                  OR name LIKE ? COLLATE NOCASE
                  OR brand LIKE ? COLLATE NOCASE
              );
            """,
            (query, search_pattern, search_pattern),
        ).fetchone()[0]

    def list_bar_codes(self) -> set[str]:
        """DEMO: retorna códigos já persistidos para carga idempotente.

        Pré-condição: a tabela products deve existir.
        Pós-condição: retorna um conjunto com todos os códigos cadastrados.
        """
        rows = self.connection.execute("SELECT bar_code FROM products;").fetchall()
        return {row[0] for row in rows}

    def add_products(self, products: list[tuple[Product, int]]) -> None:
        """DEMO: persiste vários produtos em uma única transação.

        Pré-condição: produtos e quantidades devem ser válidos e únicos.
        Pós-condição: todos os registros são inseridos e confirmados.
        """
        for _, quantity in products:
            validate_quantity(quantity)
        self.connection.executemany(
            """
            INSERT INTO products (bar_code, name, brand, price, quantity)
            VALUES (?, ?, ?, ?, ?);
            """,
            [
                (
                    product.bar_code,
                    product.name,
                    product.brand,
                    product.price,
                    quantity,
                )
                for product, quantity in products
            ],
        )
        self.connection.commit()

    def update_product(self, product: Product) -> None:
        """AD02: persiste nome, marca e preço de um produto.

        Pré-condição: product deve ser válido e já estar cadastrado.
        Pós-condição: os dados editáveis são atualizados e confirmados.
        """
        self.connection.execute(
            """
            UPDATE products
            SET name = ?, brand = ?, price = ?
            WHERE bar_code = ?;
            """,
            (
                product.name,
                product.brand,
                product.price,
                product.bar_code,
            ),
        )
        self.connection.commit()

    def deactivate_product(self, bar_code: str) -> None:
        """AD02: marca um produto como inativo sem apagar sua linha.

        Pré-condição: bar_code deve identificar um produto cadastrado.
        Pós-condição: o registro permanece no banco com active igual a zero.
        """
        self.connection.execute(
            """
            UPDATE products
            SET active = 0
            WHERE bar_code = ?;
            """,
            (bar_code,),
        )
        self.connection.commit()

    def update_stock(self, bar_code: str, quantity: int) -> None:
        """AD03: persiste a quantidade em estoque de um produto.

        Pré-condição: bar_code deve existir e quantity deve ser não negativa.
        Pós-condição: a nova quantidade é atualizada e confirmada.
        """
        validate_quantity(quantity)
        self.connection.execute(
            """
            UPDATE products
            SET quantity = ?
            WHERE bar_code = ?;
            """,
            (quantity, bar_code),
        )
        self.connection.commit()

    def _ensure_active_column(self) -> None:
        """AD02: adiciona active a bancos criados antes da remoção lógica."""
        columns = self.connection.execute("PRAGMA table_info(products);").fetchall()
        column_names = {column[1] for column in columns}

        if "active" not in column_names:
            self.connection.execute(
                """
                ALTER TABLE products
                ADD COLUMN active INTEGER NOT NULL DEFAULT 1;
                """
            )

    @staticmethod
    def _to_product_with_quantity(row) -> tuple[Product, int]:
        """US02: converte uma linha SQLite em produto e quantidade."""
        product = Product(
            name=row[1],
            brand=row[2],
            price=row[3],
            bar_code=row[0],
        )
        return product, row[4]
