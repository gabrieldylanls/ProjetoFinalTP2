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
            latitude=-15.793889,
            longitude=-47.882778,
        )

        self.assertEqual(store.store_id, 1)
        self.assertEqual(store.latitude, -15.793889)
        self.assertEqual(store.longitude, -47.882778)
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

    def test_us06_gps_find_nearest_store(self):
        """US06/GPS: deve retornar a loja mais próxima por latitude e longitude."""
        far_store = self.service.create_store(
            name="Mercado Distante",
            address="Taguatinga",
            latitude=-15.832,
            longitude=-48.057,
        )
        near_store = self.service.create_store(
            name="Mercado Próximo",
            address="Asa Sul",
            latitude=-15.794,
            longitude=-47.883,
        )

        store, distance_km = self.service.find_nearest_store(
            latitude=-15.793889,
            longitude=-47.882778,
        )

        self.assertEqual(store, near_store)
        self.assertLess(distance_km, 1)
        self.assertNotEqual(store, far_store)
