import unittest
from datetime import datetime, timezone

from app.application.shopping_list_service import ShoppingListService
from app.domain.exceptions import (
    InvalidShoppingListError,
    ProductNotFoundError,
    ShoppingListItemNotFoundError,
    ShoppingListNotFoundError,
)
from app.domain.product import Product


class FakeShoppingListRepository:
    """Simula a persistência de listas de compras em memória."""

    def __init__(self):
        self.shopping_lists = []

    def add_shopping_list(self, shopping_list):
        shopping_list.list_id = len(self.shopping_lists) + 1
        self.shopping_lists.append(shopping_list)

    def get_shopping_list_by_id(self, list_id):
        return next(
            (
                shopping_list
                for shopping_list in self.shopping_lists
                if shopping_list.list_id == list_id
            ),
            None,
        )

    def add_item(self, item):
        self.items[(item.list_id, item.bar_code)] = item

    def update_item(self, item):
        self.items[(item.list_id, item.bar_code)] = item

    def get_item(self, list_id, bar_code):
        return self.items.get((list_id, bar_code))

    def remove_item(self, list_id, bar_code):
        del self.items[(list_id, bar_code)]


class FakeProductRepository:
    """Simula os produtos disponíveis para inclusão em listas."""

    def __init__(self):
        self.products = {}

    def add_product(self, product, quantity):
        self.products[product.bar_code] = (product, quantity)

    def get_product_by_bar_code(self, bar_code):
        return self.products.get(bar_code)


class TestUS03ShoppingListService(unittest.TestCase):
    """US03: testa a criação de listas de compras."""

    def setUp(self):
        self.repository = FakeShoppingListRepository()
        self.repository.items = {}
        self.product_repository = FakeProductRepository()
        self.created_at = datetime(
            2026,
            6,
            19,
            12,
            0,
            tzinfo=timezone.utc,
        )
        self.service = ShoppingListService(
            self.repository,
            product_repository=self.product_repository,
            clock=lambda: self.created_at,
        )

    def test_us03_create_shopping_list_for_user(self):
        """US03: deve associar a nova lista ao usuário informado."""
        shopping_list = self.service.create_shopping_list(
            user_id=7,
            name="Compras da semana",
        )

        self.assertEqual(shopping_list.list_id, 1)
        self.assertEqual(shopping_list.user_id, 7)
        self.assertEqual(shopping_list.name, "Compras da semana")
        self.assertEqual(shopping_list.created_at, self.created_at)
        self.assertIs(self.repository.shopping_lists[0], shopping_list)

    def test_us03_reject_empty_name_without_persisting(self):
        """US03: nome vazio deve ser rejeitado sem salvar a lista."""
        with self.assertRaises(InvalidShoppingListError):
            self.service.create_shopping_list(user_id=7, name=" ")

        self.assertEqual(self.repository.shopping_lists, [])

    def create_list_and_product(self):
        """US03: prepara lista e produto válidos para testes de itens."""
        shopping_list = self.service.create_shopping_list(
            user_id=7,
            name="Compras da semana",
        )
        product = Product(
            name="Arroz Integral",
            brand="Tio João",
            price=12.50,
            bar_code="1234567890444",
        )
        self.product_repository.add_product(product, quantity=8)
        return shopping_list, product

    def test_us03_add_product_to_owned_list(self):
        """US03: deve adicionar produto existente à lista do usuário."""
        shopping_list, product = self.create_list_and_product()

        item = self.service.add_item(
            user_id=7,
            list_id=shopping_list.list_id,
            bar_code=product.bar_code,
            quantity=2,
        )

        self.assertEqual(item.list_id, shopping_list.list_id)
        self.assertEqual(item.bar_code, product.bar_code)
        self.assertEqual(item.quantity, 2)
        self.assertIs(
            self.repository.items[(shopping_list.list_id, product.bar_code)],
            item,
        )

    def test_us03_reject_missing_product(self):
        """US03: deve rejeitar produto inexistente com erro controlado."""
        shopping_list = self.service.create_shopping_list(
            user_id=7,
            name="Compras da semana",
        )

        with self.assertRaises(ProductNotFoundError):
            self.service.add_item(
                user_id=7,
                list_id=shopping_list.list_id,
                bar_code="9999999999999",
                quantity=2,
            )

    def test_us03_reject_non_positive_item_quantity(self):
        """US03: deve rejeitar quantidade de item menor ou igual a zero."""
        shopping_list, product = self.create_list_and_product()

        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(
                    InvalidShoppingListError,
                    "^A quantidade do item deve ser maior que zero\\.$",
                ):
                    self.service.add_item(
                        user_id=7,
                        list_id=shopping_list.list_id,
                        bar_code=product.bar_code,
                        quantity=quantity,
                    )

    def test_us03_update_existing_item_quantity(self):
        """US03: deve alterar a quantidade de item existente."""
        shopping_list, product = self.create_list_and_product()
        self.service.add_item(
            user_id=7,
            list_id=shopping_list.list_id,
            bar_code=product.bar_code,
            quantity=2,
        )

        item = self.service.update_item(
            user_id=7,
            list_id=shopping_list.list_id,
            bar_code=product.bar_code,
            quantity=5,
        )

        self.assertEqual(item.quantity, 5)
        self.assertEqual(
            self.repository.get_item(
                shopping_list.list_id,
                product.bar_code,
            ).quantity,
            5,
        )

    def test_us03_remove_existing_item(self):
        """US03: deve remover item existente da lista."""
        shopping_list, product = self.create_list_and_product()
        self.service.add_item(
            user_id=7,
            list_id=shopping_list.list_id,
            bar_code=product.bar_code,
            quantity=2,
        )

        self.service.remove_item(
            user_id=7,
            list_id=shopping_list.list_id,
            bar_code=product.bar_code,
        )

        self.assertIsNone(
            self.repository.get_item(
                shopping_list.list_id,
                product.bar_code,
            )
        )

    def test_us03_reject_changes_to_another_users_list(self):
        """US03: usuário não deve alterar lista pertencente a outro usuário."""
        shopping_list, product = self.create_list_and_product()

        with self.assertRaises(ShoppingListNotFoundError):
            self.service.add_item(
                user_id=8,
                list_id=shopping_list.list_id,
                bar_code=product.bar_code,
                quantity=2,
            )

    def test_us03_reject_update_or_removal_of_missing_item(self):
        """US03: deve rejeitar alteração ou remoção de item inexistente."""
        shopping_list, product = self.create_list_and_product()

        with self.assertRaises(ShoppingListItemNotFoundError):
            self.service.update_item(
                user_id=7,
                list_id=shopping_list.list_id,
                bar_code=product.bar_code,
                quantity=3,
            )
        with self.assertRaises(ShoppingListItemNotFoundError):
            self.service.remove_item(
                user_id=7,
                list_id=shopping_list.list_id,
                bar_code=product.bar_code,
            )
