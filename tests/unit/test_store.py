import unittest

from app.domain.exceptions import InvalidStoreError
from app.domain.store import Store


class TestUS06Store(unittest.TestCase):
    """US06: testa as regras do local de compra."""

    def test_us06_create_valid_store(self):
        """US06: deve criar local com nome, endereço e observação."""
        store = Store(
            store_id=1,
            name="Mercado Central",
            address="Rua Principal, 100",
            observation="Aberto aos domingos",
        )

        self.assertEqual(store.store_id, 1)
        self.assertEqual(store.name, "Mercado Central")
        self.assertEqual(store.address, "Rua Principal, 100")
        self.assertEqual(store.observation, "Aberto aos domingos")

    def test_us06_optional_observation_defaults_to_none(self):
        """US06: observação deve ser opcional."""
        store = Store(
            store_id=None,
            name="Mercado Central",
            address="Rua Principal, 100",
        )

        self.assertIsNone(store.observation)

    def test_us06_reject_empty_name_or_address(self):
        """US06: deve rejeitar nome e endereço vazios."""
        invalid_data = (
            ("", "Rua Principal, 100"),
            ("Mercado Central", " "),
        )

        for name, address in invalid_data:
            with self.subTest(name=name, address=address):
                with self.assertRaises(InvalidStoreError):
                    Store(
                        store_id=None,
                        name=name,
                        address=address,
                    )
