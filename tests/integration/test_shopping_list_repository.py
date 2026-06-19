import sqlite3
import unittest
from datetime import datetime, timezone

from app.domain.shopping_list import ShoppingList, ShoppingListItem
from app.infrastructure.shopping_list_repository import (
    SQLiteShoppingListRepository,
)


class TestUS03SQLiteShoppingListRepository(unittest.TestCase):
    """US03: testa a persistência SQLite de listas de compras."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.repository = SQLiteShoppingListRepository(self.connection)
        self.repository.create_table()

    def tearDown(self):
        self.connection.close()

    def test_us03_add_and_get_shopping_list(self):
        """US03: deve persistir lista associada ao usuário."""
        created_at = datetime(2026, 6, 19, 12, 0, tzinfo=timezone.utc)
        shopping_list = ShoppingList(
            list_id=None,
            user_id=7,
            name="Compras da semana",
            created_at=created_at,
        )

        self.repository.add_shopping_list(shopping_list)
        stored_list = self.repository.get_shopping_list_by_id(shopping_list.list_id)

        self.assertIsInstance(shopping_list.list_id, int)
        self.assertEqual(stored_list.user_id, 7)
        self.assertEqual(stored_list.name, "Compras da semana")
        self.assertEqual(stored_list.created_at, created_at)

    def create_persisted_list(self):
        """US03: cria e persiste uma lista para testes de itens."""
        shopping_list = ShoppingList(
            list_id=None,
            user_id=7,
            name="Compras da semana",
            created_at=datetime.now(timezone.utc),
        )
        self.repository.add_shopping_list(shopping_list)
        return shopping_list

    def test_us03_add_and_get_shopping_list_item(self):
        """US03: deve persistir produto e quantidade na lista."""
        shopping_list = self.create_persisted_list()
        item = ShoppingListItem(
            list_id=shopping_list.list_id,
            bar_code="1234567890444",
            quantity=2,
        )

        self.repository.add_item(item)
        stored_item = self.repository.get_item(
            shopping_list.list_id,
            item.bar_code,
        )

        self.assertEqual(stored_item.list_id, shopping_list.list_id)
        self.assertEqual(stored_item.bar_code, item.bar_code)
        self.assertEqual(stored_item.quantity, 2)

    def test_us03_update_shopping_list_item_quantity(self):
        """US03: deve persistir a nova quantidade do item."""
        shopping_list = self.create_persisted_list()
        item = ShoppingListItem(
            list_id=shopping_list.list_id,
            bar_code="1234567890444",
            quantity=2,
        )
        self.repository.add_item(item)
        updated_item = ShoppingListItem(
            list_id=shopping_list.list_id,
            bar_code=item.bar_code,
            quantity=5,
        )

        self.repository.update_item(updated_item)

        self.assertEqual(
            self.repository.get_item(
                shopping_list.list_id,
                item.bar_code,
            ).quantity,
            5,
        )

    def test_us03_remove_shopping_list_item(self):
        """US03: deve remover o item da lista."""
        shopping_list = self.create_persisted_list()
        item = ShoppingListItem(
            list_id=shopping_list.list_id,
            bar_code="1234567890444",
            quantity=2,
        )
        self.repository.add_item(item)

        self.repository.remove_item(
            shopping_list.list_id,
            item.bar_code,
        )

        self.assertIsNone(
            self.repository.get_item(
                shopping_list.list_id,
                item.bar_code,
            )
        )
