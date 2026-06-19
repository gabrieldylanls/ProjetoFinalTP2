import unittest

from app.application.store_service import StoreService
from app.domain.exceptions import InvalidStoreError


class FakeStoreRepository:
    """Simula a persistência de locais de compra em memória."""

    def __init__(self):
        self.stores = []

    def add_store(self, store):
        store.store_id = len(self.stores) + 1
        self.stores.append(store)

    def list_stores(self):
        return list(self.stores)


class TestUS06StoreService(unittest.TestCase):
    """US06: testa cadastro e consulta de locais de compra."""

    def setUp(self):
        self.repository = FakeStoreRepository()
        self.service = StoreService(self.repository)

    def test_us06_create_store(self):
        """US06: deve cadastrar um local válido."""
        store = self.service.create_store(
            name="Mercado Central",
            address="Rua Principal, 100",
            observation="Aberto aos domingos",
        )

        self.assertEqual(store.store_id, 1)
        self.assertIs(self.repository.stores[0], store)

    def test_us06_reject_invalid_store_without_persisting(self):
        """US06: dados inválidos não devem ser persistidos."""
        with self.assertRaises(InvalidStoreError):
            self.service.create_store(name="", address="Rua Principal, 100")

        self.assertEqual(self.repository.stores, [])

    def test_us06_list_stores(self):
        """US06: deve listar os locais cadastrados."""
        store = self.service.create_store(
            name="Mercado Central",
            address="Rua Principal, 100",
        )

        self.assertEqual(self.service.list_stores(), [store])
