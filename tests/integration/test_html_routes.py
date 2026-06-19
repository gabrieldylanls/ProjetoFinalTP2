import sqlite3
import unittest

from app.web.app import create_app


class TestWEBHtmlRoutes(unittest.TestCase):
    """WEB: testa as páginas HTML mínimas do protótipo."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()
        self._authenticate_as_admin()
        self._create_product()

    def tearDown(self):
        self.connection.close()

    def _authenticate_as_admin(self):
        """WEB: configura uma sessão administrativa para os testes."""
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
            flask_session["user_id"] = 1
            flask_session["role"] = "admin"

    def _create_product(self):
        """WEB: cadastra um produto para listagem, busca e carrinho."""
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

    def test_web_home_page(self):
        """WEB: página inicial deve responder 200 e exibir o título."""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Gerência de Compras", response.get_data(as_text=True))

    def test_web_product_listing_page(self):
        """WEB: catálogo deve responder 200 e listar produtos ativos."""
        response = self.client.get("/catalog")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Produtos", html)
        self.assertIn("Arroz Integral", html)
        self.assertIn("Tio João", html)

    def test_web_product_search_page(self):
        """WEB: busca deve exibir produtos compatíveis com o texto."""
        response = self.client.get("/catalog?q=arroz")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Resultados para", html)
        self.assertIn("Arroz Integral", html)

    def test_web_admin_gets_new_product_form(self):
        """WEB: admin deve acessar formulário de cadastro com HTTP 200."""
        response = self.client.get("/admin/products/new")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Cadastrar produto",
            response.get_data(as_text=True),
        )

    def test_web_admin_creates_product_with_form_and_redirects(self):
        """WEB: cadastro por formulário deve persistir e redirecionar."""
        response = self.client.post(
            "/admin/products/new",
            data={
                "name": "Feijão Carioca",
                "brand": "Camil",
                "price": "8.90",
                "bar_code": "1234567890555",
                "quantity": "5",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/catalog"))

        catalog_response = self.client.get("/catalog")
        self.assertIn(
            "Feijão Carioca",
            catalog_response.get_data(as_text=True),
        )

    def test_web_common_user_cannot_access_new_product_form(self):
        """WEB: usuário comum deve receber HTTP 403 no formulário admin."""
        with self.client.session_transaction() as flask_session:
            flask_session["role"] = "user"

        response = self.client.get("/admin/products/new")

        self.assertEqual(response.status_code, 403)

    def test_web_cart_page(self):
        """WEB: carrinho deve responder 200 e exibir itens da sessão."""
        self.client.post(
            "/cart/items",
            json={
                "bar_code": "1234567890444",
                "quantity": 2,
            },
        )

        response = self.client.get("/cart/view")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Carrinho", html)
        self.assertIn("Arroz Integral", html)
        self.assertIn("25.00", html)
