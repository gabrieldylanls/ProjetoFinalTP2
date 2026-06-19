import sqlite3
import unittest

from app.domain.product import Product
from app.infrastructure.product_repository import SQLitePrductRepository

class TestSQLiteProductRepository(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.repository = SQLiteProductRepository(self.connection)
        self.repository.create_table()

    def tearDown(self):
        self.connection.close()

    def test_add_and_get_product(self):

        product = Product(
            name='Test Product',
            brand='Test Brand',
            price=9.99,
            bar_code="1234567890123"
        )
        
        self.repository.add_product(product,quantity=10)

        stored_product, stored_quantity = self.repository.get_product_by_bar_code(
            "1234567890123"
        )

        self.assertEqual(stored_product.name, 'Test Product')
        self.assertEqual(stored_product.brand, 'Test Brand')
        self.assertEqual(stored_product.price, 9.99)
        self.assertEqual(stored_product.bar_code, "1234567890123")
        self.assertEqual(stored_quantity, 10)
        
  