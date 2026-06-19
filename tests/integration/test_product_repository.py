import re
import sqlite3
import unittest

from app.domain.exceptions import DuplicateBarcodeError, InvalidQuantityError
from app.domain.product import Product
from app.infrastructure.product_repository import SQLiteProductRepository


class TestSQLiteProductRepository(unittest.TestCase):
    """Testa a persistência e consulta real de produtos em SQLite."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.repository = SQLiteProductRepository(self.connection)
        self.repository.create_table()

    def tearDown(self):
        self.connection.close()

    @staticmethod
    def create_product(
        bar_code="1234567890123",
        name="Produto de teste",
    ):
        """Cria um produto válido para os testes do repositório."""
        return Product(
            name=name,
            brand="Marca de teste",
            price=9.99,
            bar_code=bar_code,
        )

    def test_add_and_get_product(self):
        """Deve salvar e recuperar produto e quantidade."""
        product = self.create_product()

        self.repository.add_product(product, quantity=10)
        stored_product, stored_quantity = self.repository.get_product_by_bar_code(
            product.bar_code
        )

        self.assertEqual(stored_product.name, "Produto de teste")
        self.assertEqual(stored_product.brand, "Marca de teste")
        self.assertEqual(stored_product.price, 9.99)
        self.assertEqual(stored_product.bar_code, "1234567890123")
        self.assertEqual(stored_quantity, 10)

    def test_get_missing_product(self):
        """Deve retornar None quando o produto não existir."""
        result = self.repository.get_product_by_bar_code("9999999999999")

        self.assertIsNone(result)

    def test_add_product_with_zero_quantity(self):
        """Deve persistir um produto com estoque zero."""
        product = self.create_product()

        self.repository.add_product(product, quantity=0)
        _, stored_quantity = self.repository.get_product_by_bar_code(product.bar_code)

        self.assertEqual(stored_quantity, 0)

    def test_reject_invalid_quantity(self):
        """Deve rejeitar quantidades inválidas sem inserir registros."""
        invalid_cases = (
            (-1, "A quantidade do produto não pode ser negativa."),
            (1.5, "A quantidade do produto deve ser um número inteiro."),
            ("5", "A quantidade do produto deve ser um número inteiro."),
            (True, "A quantidade do produto deve ser um número inteiro."),
            (None, "A quantidade do produto deve ser um número inteiro."),
            ([], "A quantidade do produto deve ser um número inteiro."),
        )

        for quantity, message in invalid_cases:
            product = self.create_product()

            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(
                    InvalidQuantityError,
                    f"^{re.escape(message)}$",
                ):
                    self.repository.add_product(product, quantity=quantity)

                self.assertIsNone(
                    self.repository.get_product_by_bar_code(product.bar_code)
                )

    def test_reject_duplicate_bar_code(self):
        """Deve rejeitar duplicidade e preservar o registro original."""
        original_product = self.create_product(name="Produto original")
        duplicate_product = self.create_product(name="Produto duplicado")
        self.repository.add_product(original_product, quantity=10)

        with self.assertRaisesRegex(
            DuplicateBarcodeError,
            "^Já existe um produto com o código de barras 1234567890123\\.$",
        ):
            self.repository.add_product(duplicate_product, quantity=20)

        stored_product, stored_quantity = self.repository.get_product_by_bar_code(
            original_product.bar_code
        )
        record_count = self.connection.execute(
            "SELECT COUNT(*) FROM products;"
        ).fetchone()[0]

        self.assertEqual(stored_product.name, "Produto original")
        self.assertEqual(stored_quantity, 10)
        self.assertEqual(record_count, 1)

    def test_us02_search_products_by_partial_name(self):
        """US02: deve buscar produtos por parte do nome."""
        rice = Product(
            name="Arroz Integral",
            brand="Tio João",
            price=12.50,
            bar_code="1234567890444",
        )
        beans = Product(
            name="Feijão Carioca",
            brand="Camil",
            price=8.90,
            bar_code="1234567890555",
        )
        self.repository.add_product(rice, quantity=8)
        self.repository.add_product(beans, quantity=5)

        results = self.repository.search_products_by_text("ARROZ")

        self.assertEqual(len(results), 1)
        product, quantity = results[0]
        self.assertEqual(product.name, "Arroz Integral")
        self.assertEqual(quantity, 8)

    def test_us02_search_products_by_partial_brand(self):
        """US02: deve buscar produtos por parte da marca."""
        rice = Product(
            name="Arroz Integral",
            brand="Tio João",
            price=12.50,
            bar_code="1234567890444",
        )
        beans = Product(
            name="Feijão Carioca",
            brand="Camil Alimentos",
            price=8.90,
            bar_code="1234567890555",
        )
        self.repository.add_product(rice, quantity=8)
        self.repository.add_product(beans, quantity=5)

        results = self.repository.search_products_by_text("camil")

        self.assertEqual(len(results), 1)
        product, quantity = results[0]
        self.assertEqual(product.brand, "Camil Alimentos")
        self.assertEqual(quantity, 5)

    def test_us02_search_without_results_returns_empty_list(self):
        """US02: busca sem correspondência deve retornar lista vazia."""
        product = self.create_product()
        self.repository.add_product(product, quantity=10)

        results = self.repository.search_products_by_text("inexistente")

        self.assertEqual(results, [])

    def test_ad02_update_existing_product(self):
        """AD02: deve persistir nome, marca e preço atualizados."""
        original_product = self.create_product()
        self.repository.add_product(original_product, quantity=10)
        updated_product = Product(
            name="Produto atualizado",
            brand="Marca atualizada",
            price=15.75,
            bar_code=original_product.bar_code,
        )

        self.repository.update_product(updated_product)

        stored_product, stored_quantity = self.repository.get_product_by_bar_code(
            original_product.bar_code
        )
        self.assertEqual(stored_product.name, "Produto atualizado")
        self.assertEqual(stored_product.brand, "Marca atualizada")
        self.assertEqual(stored_product.price, 15.75)
        self.assertEqual(stored_product.bar_code, original_product.bar_code)
        self.assertEqual(stored_quantity, 10)

    def test_ad02_create_table_adds_active_column(self):
        """AD02: tabela nova deve possuir active com valor padrão 1."""
        columns = self.connection.execute("PRAGMA table_info(products);").fetchall()
        active_column = next(column for column in columns if column[1] == "active")

        self.assertEqual(active_column[3], 1)
        self.assertEqual(active_column[4], "1")

    def test_ad02_create_table_migrates_existing_database(self):
        """AD02: banco antigo deve receber active preservando registros."""
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute(
            """
            CREATE TABLE products (
                bar_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            );
            """
        )
        connection.execute(
            """
            INSERT INTO products (bar_code, name, brand, price, quantity)
            VALUES (?, ?, ?, ?, ?);
            """,
            ("1234567890777", "Produto antigo", "Marca antiga", 5.0, 2),
        )
        connection.commit()
        repository = SQLiteProductRepository(connection)

        repository.create_table()

        active = connection.execute(
            """
            SELECT active
            FROM products
            WHERE bar_code = ?;
            """,
            ("1234567890777",),
        ).fetchone()[0]
        self.assertEqual(active, 1)

    def test_ad02_deactivate_product_without_physical_delete(self):
        """AD02: deve manter a linha inativa e ocultá-la da busca."""
        product = Product(
            name="Arroz Integral",
            brand="Tio João",
            price=12.50,
            bar_code="1234567890444",
        )
        self.repository.add_product(product, quantity=8)

        self.repository.deactivate_product(product.bar_code)

        stored_row = self.connection.execute(
            """
            SELECT active
            FROM products
            WHERE bar_code = ?;
            """,
            (product.bar_code,),
        ).fetchone()
        self.assertEqual(stored_row, (0,))
        self.assertEqual(
            self.repository.search_products_by_text("arroz"),
            [],
        )

    def test_ad03_update_product_stock(self):
        """AD03: deve persistir a nova quantidade do produto."""
        product = Product(
            name="Arroz Integral",
            brand="Tio João",
            price=12.50,
            bar_code="1234567890444",
        )
        self.repository.add_product(product, quantity=8)

        self.repository.update_stock(product.bar_code, quantity=20)

        stored_product, stored_quantity = self.repository.get_product_by_bar_code(
            product.bar_code
        )
        search_results = self.repository.search_products_by_text("arroz")
        self.assertEqual(stored_product.bar_code, product.bar_code)
        self.assertEqual(stored_quantity, 20)
        self.assertEqual(search_results[0][1], 20)
