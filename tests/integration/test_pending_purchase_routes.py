import sqlite3
import unittest

from app.web.app import create_app


class TestUS07PendingPurchaseRoutes(unittest.TestCase):
    """US07: testa itens não comprados e pendências por usuário."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()
        self.create_product_as_admin()
        self.create_store_as_admin()
        self.authenticate_user(7)

    def tearDown(self):
        self.connection.close()

    def authenticate_user(self, user_id):
        """US07: configura sessão de usuário comum."""
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
            flask_session["user_id"] = user_id
            flask_session["role"] = "user"

    def authenticate_admin(self):
        """US07: configura sessão administrativa."""
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
            flask_session["user_id"] = 1
            flask_session["role"] = "admin"

    def create_product_as_admin(self):
        """US07: cria produto para uso nas listas."""
        self.authenticate_admin()
        self.client.post(
            "/products",
            json={
                "name": "Arroz Integral",
                "brand": "Tio João",
                "price": 12.50,
                "bar_code": "1234567890444",
                "quantity": 8,
            },
        )

    def create_store_as_admin(self):
        """US07: cria local para preço observado."""
        self.authenticate_admin()
        self.client.post(
            "/stores",
            json={
                "name": "Mercado Central",
                "address": "Rua A",
                "observation": "Perto",
            },
        )

    def create_list_with_item(self, user_id=7, quantity=3):
        """US07: cria lista com item planejado."""
        self.authenticate_user(user_id)
        list_response = self.client.post(
            "/shopping-lists",
            json={"name": "Compras da semana"},
        )
        list_id = list_response.get_json()["id"]
        self.client.post(
            f"/shopping-lists/{list_id}/items",
            json={
                "bar_code": "1234567890444",
                "quantity": quantity,
            },
        )
        return list_id

    def test_us07_mark_total_item_as_pending(self):
        """US07: item total sai da lista e entra em pendentes."""
        list_id = self.create_list_with_item(quantity=3)

        response = self.client.post(
            f"/shopping-lists/{list_id}/items/1234567890444/pending",
            json={"quantity": 3},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["quantity"], 3)
        stored_list_item = self.connection.execute(
            """
            SELECT quantity
            FROM shopping_list_items
            WHERE list_id = ? AND bar_code = ?;
            """,
            (list_id, "1234567890444"),
        ).fetchone()
        self.assertIsNone(stored_list_item)
        pending = self.client.get("/pending-items")
        self.assertEqual(pending.status_code, 200)
        self.assertEqual(pending.get_json()[0]["product"]["name"], "Arroz Integral")

    def test_us07_mark_partial_item_as_pending(self):
        """US07: quantidade parcial reduz lista e soma pendência."""
        list_id = self.create_list_with_item(quantity=5)

        response = self.client.post(
            f"/shopping-lists/{list_id}/items/1234567890444/pending",
            json={"quantity": 2},
        )

        self.assertEqual(response.status_code, 201)
        stored_quantity = self.connection.execute(
            """
            SELECT quantity
            FROM shopping_list_items
            WHERE list_id = ? AND bar_code = ?;
            """,
            (list_id, "1234567890444"),
        ).fetchone()[0]
        self.assertEqual(stored_quantity, 3)
        self.assertEqual(response.get_json()["quantity"], 2)

    def test_us07_reject_another_users_list(self):
        """US07: usuário não deve mover item de lista alheia."""
        list_id = self.create_list_with_item(user_id=7, quantity=2)
        self.authenticate_user(8)

        response = self.client.post(
            f"/shopping-lists/{list_id}/items/1234567890444/pending",
            json={"quantity": 1},
        )

        self.assertEqual(response.status_code, 404)

    def test_us07_reject_invalid_pending_quantity(self):
        """US07: quantidade inválida ou maior que a lista deve retornar 400."""
        list_id = self.create_list_with_item(quantity=2)

        for quantity in (0, -1, 3):
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    f"/shopping-lists/{list_id}/items/1234567890444/pending",
                    json={"quantity": quantity},
                )
                self.assertEqual(response.status_code, 400)

    def test_us07_pending_items_include_lowest_observed_price(self):
        """US07: pendências mostram menor preço e local quando houver."""
        list_id = self.create_list_with_item(quantity=1)
        self.client.post(
            "/prices",
            json={
                "product_bar_code": "1234567890444",
                "store_id": 1,
                "price": 10.25,
            },
        )
        self.client.post(
            f"/shopping-lists/{list_id}/items/1234567890444/pending",
            json={"quantity": 1},
        )

        response = self.client.get("/pending-items")

        self.assertEqual(response.status_code, 200)
        best_price = response.get_json()[0]["best_price"]
        self.assertEqual(best_price["price"], 10.25)
        self.assertEqual(best_price["store_name"], "Mercado Central")

    def test_us07_update_and_remove_pending_item(self):
        """US07: usuário atualiza e resolve uma pendência própria."""
        list_id = self.create_list_with_item(quantity=3)
        self.client.post(
            f"/shopping-lists/{list_id}/items/1234567890444/pending",
            json={"quantity": 1},
        )

        update_response = self.client.patch(
            "/pending-items/1234567890444",
            json={"quantity": 2},
        )
        delete_response = self.client.delete("/pending-items/1234567890444")
        list_response = self.client.get("/pending-items")

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["quantity"], 2)
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(list_response.get_json(), [])
