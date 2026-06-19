import sqlite3
import unittest

from app.web.app import create_app


class TestUS04CartRoutes(unittest.TestCase):
    """US04: testa o carrinho mantido na sessão Flask."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()
        self.create_product()

    def tearDown(self):
        self.connection.close()

    def create_product(self):
        """US04: cadastra um produto existente para os testes do carrinho."""
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
        with self.client.session_transaction() as flask_session:
            flask_session.clear()

    def test_us04_empty_cart(self):
        """US04: GET /cart deve retornar lista vazia inicialmente."""
        response = self.client.get("/cart")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_us04_add_product_to_cart_and_keep_in_session(self):
        """US04: deve adicionar produto existente e persistir na sessão."""
        response = self.client.post(
            "/cart/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )
        cart_response = self.client.get("/cart")

        expected_item = {
            "name": "Arroz Integral",
            "brand": "Tio João",
            "price": 12.50,
            "bar_code": "1234567890444",
            "quantity": 2,
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), expected_item)
        self.assertEqual(cart_response.get_json(), [expected_item])
        with self.client.session_transaction() as flask_session:
            self.assertEqual(
                flask_session["cart"]["1234567890444"],
                2,
            )

    def test_us04_reject_missing_product(self):
        """US04: produto inexistente deve retornar HTTP 404."""
        response = self.client.post(
            "/cart/items",
            json={
                "bar_code": "9999999999999",
                "quantity": 2,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.get("/cart").get_json(), [])

    def test_us04_reject_invalid_quantity(self):
        """US04: quantidade menor ou igual a zero deve retornar HTTP 400."""
        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    "/cart/items",
                    json={
                        "bar_code": "1234567890444",
                        "quantity": quantity,
                    },
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.get_json()["erro"],
                    "A quantidade do carrinho deve ser maior que zero.",
                )

    def test_us04_update_cart_item_quantity(self):
        """US04: PATCH deve alterar a quantidade do item."""
        self.client.post(
            "/cart/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        response = self.client.patch(
            "/cart/items/1234567890444",
            json={"quantity": 5},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["quantity"], 5)
        self.assertEqual(self.client.get("/cart").get_json()[0]["quantity"], 5)

    def test_us04_remove_cart_item(self):
        """US04: DELETE deve remover o item e retornar HTTP 204."""
        self.client.post(
            "/cart/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        response = self.client.delete("/cart/items/1234567890444")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")
        self.assertEqual(self.client.get("/cart").get_json(), [])
