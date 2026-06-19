import unittest
from datetime import datetime

from app.application.product_price_service import ProductPriceService
from app.domain.exceptions import (
    InvalidProductPriceError,
    ProductNotFoundError,
    StoreNotFoundError,
)
from app.domain.product import Product
from app.domain.store import Store


class FakeProductRepository:
    """US06: simula a consulta de produtos cadastrados."""

    def __init__(self):
        self.product = Product(
            name="Arroz",
            brand="Marca A",
            price=10.0,
            bar_code="1234567890123",
        )

    def get_product_by_bar_code(self, bar_code):
        """US06: retorna o produto conhecido ou None."""
        if bar_code == self.product.bar_code:
            return self.product, 5
        return None


class FakeStoreRepository:
    """US06: simula a consulta de locais cadastrados."""

    def __init__(self):
        self.store = Store(
            store_id=3,
            name="Mercado Central",
            address="Rua Principal, 100",
        )

    def get_store_by_id(self, store_id):
        """US06: retorna o local conhecido ou None."""
        if store_id == self.store.store_id:
            return self.store
        return None


class FakeProductPriceRepository:
    """US06: mantém um histórico de preços em memória."""

    def __init__(self):
        self.prices = []

    def add_price(self, product_price):
        """US06: adiciona um preço ao histórico."""
        self.prices.append(product_price)

    def list_prices_by_product(self, product_bar_code):
        """US06: lista preços vinculados ao produto informado."""
        return [
            price for price in self.prices if price.product_bar_code == product_bar_code
        ]


class TestUS06ProductPriceService(unittest.TestCase):
    """US06: testa o registro e a consulta de preços observados."""

    def setUp(self):
        self.price_repository = FakeProductPriceRepository()
        self.service = ProductPriceService(
            price_repository=self.price_repository,
            product_repository=FakeProductRepository(),
            store_repository=FakeStoreRepository(),
        )

    def test_us06_register_product_price(self):
        """US06: usuário deve registrar preço para produto e local existentes."""
        product_price = self.service.register_price(
            product_bar_code="1234567890123",
            store_id=3,
            user_id=7,
            price=8.75,
        )

        self.assertEqual(product_price.product_bar_code, "1234567890123")
        self.assertEqual(product_price.store_id, 3)
        self.assertEqual(product_price.user_id, 7)
        self.assertEqual(product_price.price, 8.75)
        self.assertIsInstance(product_price.created_at, datetime)
        self.assertEqual(self.price_repository.prices, [product_price])

    def test_us06_reject_missing_product(self):
        """US06: produto inexistente deve impedir o registro do preço."""
        with self.assertRaises(ProductNotFoundError):
            self.service.register_price(
                product_bar_code="9999999999999",
                store_id=3,
                user_id=7,
                price=8.75,
            )

        self.assertEqual(self.price_repository.prices, [])

    def test_us06_reject_missing_store(self):
        """US06: local inexistente deve impedir o registro do preço."""
        with self.assertRaises(StoreNotFoundError):
            self.service.register_price(
                product_bar_code="1234567890123",
                store_id=99,
                user_id=7,
                price=8.75,
            )

        self.assertEqual(self.price_repository.prices, [])

    def test_us06_reject_negative_price(self):
        """US06: preço negativo deve ser rejeitado antes da persistência."""
        with self.assertRaises(InvalidProductPriceError):
            self.service.register_price(
                product_bar_code="1234567890123",
                store_id=3,
                user_id=7,
                price=-0.01,
            )

        self.assertEqual(self.price_repository.prices, [])

    def test_us06_list_product_price_history(self):
        """US06: consulta deve retornar o histórico do produto."""
        registered_price = self.service.register_price(
            product_bar_code="1234567890123",
            store_id=3,
            user_id=7,
            price=8.75,
        )

        prices = self.service.list_product_prices("1234567890123")

        self.assertEqual(prices, [registered_price])

    def test_us06_reject_price_history_for_missing_product(self):
        """US06: consulta de produto inexistente deve gerar erro controlado."""
        with self.assertRaises(ProductNotFoundError):
            self.service.list_product_prices("9999999999999")
