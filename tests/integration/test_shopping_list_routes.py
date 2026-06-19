import sqlite3
import unittest

from app.web.app import create_app


class TestUS03ShoppingListRoutes(unittest.TestCase):
    """US03: testa a criação HTTP de listas de compras."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()

    def tearDown(self):
        self.connection.close()

    def authenticate_user(self, user_id=7):
        """US03: configura uma sessão de usuário autenticado."""
        with self.client.session_transaction() as flask_session:
            flask_session["user_id"] = user_id
            flask_session["role"] = "user"

    def create_product_as_admin(self):
        """US03: cadastra produto existente para manutenção de itens."""
        with self.client.session_transaction() as flask_session:
            flask_session["user_id"] = 1
            flask_session["role"] = "admin"
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

    def create_list_for_user(self, user_id=7):
        """US03: cria lista autenticada e retorna seu identificador."""
        self.authenticate_user(user_id)
        response = self.client.post(
            "/shopping-lists",
            json={"name": "Compras da semana"},
        )
        return response.get_json()["id"]

    def test_us03_authenticated_user_creates_shopping_list(self):
        """US03: usuário autenticado deve criar lista e receber HTTP 201."""
        self.authenticate_user(user_id=7)

        response = self.client.post(
            "/shopping-lists",
            json={"name": "Compras da semana"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIsInstance(data["id"], int)
        self.assertEqual(data["user_id"], 7)
        self.assertEqual(data["name"], "Compras da semana")
        self.assertIsInstance(data["created_at"], str)

        stored_user_id = self.connection.execute(
            """
            SELECT user_id
            FROM shopping_lists
            WHERE id = ?;
            """,
            (data["id"],),
        ).fetchone()[0]
        self.assertEqual(stored_user_id, 7)

    def test_us03_reject_empty_name_route(self):
        """US03: nome vazio deve retornar HTTP 400."""
        self.authenticate_user()

        response = self.client.post(
            "/shopping-lists",
            json={"name": " "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["erro"],
            "O nome da lista de compras não pode estar vazio.",
        )

    def test_us03_reject_unauthenticated_user_route(self):
        """US03: visitante deve receber HTTP 401."""
        response = self.client.post(
            "/shopping-lists",
            json={"name": "Compras da semana"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json()["erro"],
            "Autenticação necessária.",
        )

    def test_us03_add_product_to_shopping_list_route(self):
        """US03: deve adicionar produto existente à lista do usuário."""
        self.create_product_as_admin()
        list_id = self.create_list_for_user(user_id=7)

        response = self.client.post(
            f"/shopping-lists/{list_id}/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json(),
            {
                "list_id": list_id,
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

    def test_us03_reject_missing_product_route(self):
        """US03: produto inexistente deve retornar HTTP 404."""
        list_id = self.create_list_for_user(user_id=7)

        response = self.client.post(
            f"/shopping-lists/{list_id}/items",
            json={
                "bar_code": "9999999999999",
                "quantity": 2,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_us03_reject_non_positive_quantity_route(self):
        """US03: quantidade menor ou igual a zero deve retornar HTTP 400."""
        self.create_product_as_admin()
        list_id = self.create_list_for_user(user_id=7)

        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    f"/shopping-lists/{list_id}/items",
                    json={
                        "bar_code": "1234567890444",
                        "quantity": quantity,
                    },
                )
                self.assertEqual(response.status_code, 400)

    def test_us03_update_item_quantity_route(self):
        """US03: PATCH deve alterar a quantidade do item."""
        self.create_product_as_admin()
        list_id = self.create_list_for_user(user_id=7)
        self.client.post(
            f"/shopping-lists/{list_id}/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        response = self.client.patch(
            f"/shopping-lists/{list_id}/items/1234567890444",
            json={"quantity": 5},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["quantity"], 5)

    def test_us03_remove_item_route(self):
        """US03: DELETE deve remover item existente e retornar HTTP 204."""
        self.create_product_as_admin()
        list_id = self.create_list_for_user(user_id=7)
        self.client.post(
            f"/shopping-lists/{list_id}/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        response = self.client.delete(f"/shopping-lists/{list_id}/items/1234567890444")

        self.assertEqual(response.status_code, 204)
        stored_item = self.connection.execute(
            """
            SELECT quantity
            FROM shopping_list_items
            WHERE list_id = ? AND bar_code = ?;
            """,
            (list_id, "1234567890444"),
        ).fetchone()
        self.assertIsNone(stored_item)

    def test_us03_reject_changes_to_another_users_list_route(self):
        """US03: usuário não deve alterar lista de outro usuário."""
        self.create_product_as_admin()
        list_id = self.create_list_for_user(user_id=7)
        self.authenticate_user(user_id=8)

        response = self.client.post(
            f"/shopping-lists/{list_id}/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        self.assertEqual(response.status_code, 404)
