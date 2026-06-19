import sqlite3
import unittest

from app.domain.store import Store
from app.infrastructure.store_repository import SQLiteStoreRepository


class TestUS06SQLiteStoreRepository(unittest.TestCase):
    """US06: testa a persistência SQLite de locais de compra."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.repository = SQLiteStoreRepository(self.connection)
        self.repository.create_table()

    def tearDown(self):
        self.connection.close()

    def test_us06_add_and_list_stores(self):
        """US06: deve persistir e listar locais por nome."""
        second_store = Store(
            store_id=None,
            name="Supermercado B",
            address="Avenida Dois, 20",
            observation=None,
        )
        first_store = Store(
            store_id=None,
            name="Mercado A",
            address="Rua Um, 10",
            observation="24 horas",
        )

        self.repository.add_store(second_store)
        self.repository.add_store(first_store)
        stores = self.repository.list_stores()

        self.assertIsInstance(first_store.store_id, int)
        self.assertEqual(
            [store.name for store in stores],
            [
                "Mercado A",
                "Supermercado B",
            ],
        )
        self.assertEqual(stores[0].address, "Rua Um, 10")
        self.assertEqual(stores[0].observation, "24 horas")
