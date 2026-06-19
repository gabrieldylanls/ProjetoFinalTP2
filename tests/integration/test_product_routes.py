import sqlite3
import unittest

from app.web.app import create_app


class TestProductRoutes(unittest.TestCase):
    """Testa as estórias AD01, US02 e AD02 pela API Flask."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.app = create_app(self.conn)
        self.client = self.app.test_client()

    def tearDown(self):
        self.conn.close()

    def test_ad01_create_product_route(self):
        """AD01: produto válido deve retornar HTTP 201 e todos os campos."""
        response = self.client.post(
            "/products",
            json={
                "name": "Arroz",
                "brand": "Tio João",
                "price": 25.90,
                "bar_code": "1234567890123",
                "quantity": 10,
            },
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertEqual(data["name"], "Arroz")
        self.assertEqual(data["brand"], "Tio João")
        self.assertEqual(data["price"], 25.90)
        self.assertEqual(data["bar_code"], "1234567890123")
        self.assertEqual(data["quantity"], 10)

    def test_ad01_reject_duplicate_bar_code_route(self):
        """AD01: código de barras duplicado deve retornar HTTP 409."""
        payload = {
            "name": "Arroz",
            "brand": "Tio João",
            "price": 25.90,
            "bar_code": "1234567890123",
            "quantity": 10,
        }

        self.client.post("/products", json=payload)
        response = self.client.post("/products", json=payload)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.get_json()["erro"],
            "Já existe um produto com o código de barras 1234567890123.",
        )

    def test_ad01_reject_invalid_product_route(self):
        """AD01: dados inválidos devem retornar HTTP 400."""
        response = self.client.post(
            "/products",
            json={
                "name": "",
                "brand": "Tio João",
                "price": 25.90,
                "bar_code": "1234567890123",
                "quantity": 10,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["erro"],
            "O nome do produto não pode estar vazio.",
        )

    def test_ad01_reject_missing_field_route(self):
        """AD01: campo obrigatório ausente deve retornar HTTP 400."""
        response = self.client.post(
            "/products",
            json={
                "name": "Arroz",
                "brand": "Tio João",
                "price": 25.90,
                "bar_code": "1234567890123",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["erro"],
            "O campo 'quantity' é obrigatório.",
        )

    def test_us02_search_products_route(self):
        """US02: GET /products deve buscar por parte do nome."""
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
        self.client.post(
            "/products",
            json={
                "name": "Feijão Carioca",
                "brand": "Camil",
                "price": 8.90,
                "bar_code": "1234567890555",
                "quantity": 5,
            },
        )

        response = self.client.get("/products?q=arroz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [
                {
                    "name": "Arroz Integral",
                    "brand": "Tio João",
                    "price": 12.50,
                    "bar_code": "1234567890444",
                    "quantity": 8,
                }
            ],
        )

    def test_us02_search_products_by_brand_route(self):
        """US02: GET /products deve buscar por parte da marca."""
        self.client.post(
            "/products",
            json={
                "name": "Feijão Carioca",
                "brand": "Camil Alimentos",
                "price": 8.90,
                "bar_code": "1234567890555",
                "quantity": 5,
            },
        )

        response = self.client.get("/products?q=camil")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["brand"], "Camil Alimentos")

    def test_us02_search_without_results_returns_empty_list(self):
        """US02: busca sem resultado deve retornar lista vazia e HTTP 200."""
        response = self.client.get("/products?q=inexistente")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_us02_empty_query_returns_empty_list(self):
        """US02: query vazia deve retornar lista vazia e HTTP 200."""
        response = self.client.get("/products?q=")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_ad02_update_existing_product_route(self):
        """AD02: PUT deve editar produto existente e retornar HTTP 200."""
        self.client.post(
            "/products",
            json={
                "name": "Arroz",
                "brand": "Tio João",
                "price": 25.90,
                "bar_code": "1234567890123",
                "quantity": 10,
            },
        )

        response = self.client.put(
            "/products/1234567890123",
            json={
                "name": "Arroz Integral",
                "brand": "Nova Marca",
                "price": 30.50,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "name": "Arroz Integral",
                "brand": "Nova Marca",
                "price": 30.50,
                "bar_code": "1234567890123",
                "quantity": 10,
            },
        )

    def test_ad02_update_missing_product_route(self):
        """AD02: edição de produto inexistente deve retornar HTTP 404."""
        response = self.client.put(
            "/products/9999999999999",
            json={
                "name": "Produto atualizado",
                "brand": "Marca atualizada",
                "price": 30.50,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json()["erro"],
            "Produto com o código de barras 9999999999999 não encontrado.",
        )

    def test_ad02_reject_invalid_update_route(self):
        """AD02: dados inválidos na edição devem retornar HTTP 400."""
        self.client.post(
            "/products",
            json={
                "name": "Arroz",
                "brand": "Tio João",
                "price": 25.90,
                "bar_code": "1234567890123",
                "quantity": 10,
            },
        )

        response = self.client.put(
            "/products/1234567890123",
            json={
                "name": "",
                "brand": "Nova Marca",
                "price": 30.50,
            },
        )

        self.assertEqual(response.status_code, 400)

        stored_product = self.conn.execute(
            """
            SELECT name, brand, price
            FROM products
            WHERE bar_code = ?;
            """,
            ("1234567890123",),
        ).fetchone()
        self.assertEqual(stored_product, ("Arroz", "Tio João", 25.90))

    def test_ad02_deactivate_existing_product_route(self):
        """AD02: DELETE deve desativar produto e retornar HTTP 204."""
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

        response = self.client.delete("/products/1234567890444")
        search_response = self.client.get("/products?q=arroz")
        stored_row = self.conn.execute(
            """
            SELECT active
            FROM products
            WHERE bar_code = ?;
            """,
            ("1234567890444",),
        ).fetchone()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.get_json(), [])
        self.assertEqual(stored_row, (0,))

    def test_ad02_deactivate_missing_product_route(self):
        """AD02: remoção de produto inexistente deve retornar HTTP 404."""
        response = self.client.delete("/products/9999999999999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json()["erro"],
            "Produto com o código de barras 9999999999999 não encontrado.",
        )
