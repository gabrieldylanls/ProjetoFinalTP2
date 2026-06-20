import sqlite3
import unittest

from app.web.app import create_app


class TestWEBMvpHtmlRoutes(unittest.TestCase):
    """US01/US04/US06/WEB: testa os fluxos principais do site."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()
        self._create_product()
        self.store_id = self._create_store()

    def tearDown(self):
        self.connection.close()

    def authenticate_as(self, role="user", user_id=7):
        """WEB: configura uma sessão autenticada para o teste."""
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
            flask_session["user_id"] = user_id
            flask_session["role"] = role

    def _create_product(self):
        """WEB: cadastra um produto para os fluxos do site."""
        self.authenticate_as("admin", 1)
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

    def _create_store(self):
        """US06/WEB: cadastra um local para os fluxos do site."""
        response = self.client.post(
            "/stores",
            json={
                "name": "Mercado Central",
                "address": "Rua Principal, 100",
            },
        )
        return response.get_json()["id"]

    def test_us01_web_register_page_creates_common_user(self):
        """US01/WEB: cadastro público deve criar somente usuário comum."""
        get_response = self.client.get("/register")
        post_response = self.client.post(
            "/register",
            data={
                "name": "Joana Silva",
                "email": "joana@example.com",
                "password": "senha-segura",
            },
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertIn("Criar conta", get_response.get_data(as_text=True))
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(post_response.headers["Location"].endswith("/dashboard"))
        role = self.connection.execute(
            "SELECT role FROM users WHERE email = 'joana@example.com';"
        ).fetchone()[0]
        self.assertEqual(role, "user")

    def test_us01_web_register_duplicate_email_returns_html_error(self):
        """US01/WEB: e-mail duplicado deve permanecer no formulário."""
        payload = {
            "name": "Joana Silva",
            "email": "joana@example.com",
            "password": "senha-segura",
        }
        self.client.post("/register", data=payload)

        response = self.client.post("/register", data=payload)

        self.assertEqual(response.status_code, 409)
        self.assertIn(
            "Já existe um usuário",
            response.get_data(as_text=True),
        )

    def test_web_authenticated_user_dashboard(self):
        """WEB: usuário autenticado deve acessar seu painel."""
        self.authenticate_as("user")

        response = self.client.get("/dashboard")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Meu painel", html)
        self.assertIn("Explorar produtos", html)
        self.assertIn("Locais de compra", html)

    def test_us06_web_admin_creates_store_with_form(self):
        """US06/WEB: admin deve cadastrar loja por formulário HTML."""
        self.authenticate_as("admin")

        response = self.client.post(
            "/admin/stores/new",
            data={
                "name": "Supermercado Avenida",
                "address": "Avenida Central, 500",
                "observation": "Aberto até 22h",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/stores/view"))
        stored = self.connection.execute(
            """
            SELECT name, address
            FROM stores
            WHERE name = 'Supermercado Avenida';
            """
        ).fetchone()
        self.assertEqual(stored, ("Supermercado Avenida", "Avenida Central, 500"))

    def test_us06_web_user_registers_product_price_with_form(self):
        """US06/WEB: usuário deve compartilhar preço por loja."""
        self.authenticate_as("user")

        response = self.client.post(
            "/products/1234567890444/prices/new",
            data={
                "store_id": str(self.store_id),
                "price": "10.90",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.headers["Location"].endswith(
                "/products/1234567890444/view"
            )
        )
        stored_price = self.connection.execute(
            """
            SELECT price
            FROM product_prices
            WHERE product_bar_code = '1234567890444';
            """
        ).fetchone()[0]
        self.assertEqual(stored_price, 10.90)

    def test_us06_web_product_detail_lists_prices_by_store(self):
        """US06/WEB: detalhe deve exibir preços e nomes das lojas."""
        self.authenticate_as("user")
        self.client.post(
            "/products/1234567890444/prices/new",
            data={
                "store_id": str(self.store_id),
                "price": "10.90",
            },
        )

        response = self.client.get("/products/1234567890444/view")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Arroz Integral", html)
        self.assertIn("Mercado Central", html)
        self.assertIn("10.90", html)

    def test_us06_web_catalog_filters_products_by_store(self):
        """US06/WEB: catálogo deve filtrar produtos observados na loja."""
        self.authenticate_as("user")
        self.client.post(
            "/products/1234567890444/prices/new",
            data={
                "store_id": str(self.store_id),
                "price": "10.90",
            },
        )

        response = self.client.get(f"/catalog?store_id={self.store_id}")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Mercado Central", html)
        self.assertIn("Arroz Integral", html)
        self.assertIn("R$ 10.90", html)

    def test_us04_web_cart_forms_add_update_and_remove_item(self):
        """US04/WEB: formulários devem manter o carrinho na sessão."""
        self.authenticate_as("user")

        add_response = self.client.post(
            "/cart/view/items",
            data={"bar_code": "1234567890444", "quantity": "2"},
        )
        update_response = self.client.post(
            "/cart/view/items/1234567890444/update",
            data={"quantity": "4"},
        )
        cart_response = self.client.get("/cart/view")
        remove_response = self.client.post(
            "/cart/view/items/1234567890444/remove"
        )

        self.assertEqual(add_response.status_code, 302)
        self.assertEqual(update_response.status_code, 302)
        self.assertIn("50.00", cart_response.get_data(as_text=True))
        self.assertEqual(remove_response.status_code, 302)
        self.assertIn(
            "carrinho está vazio",
            self.client.get("/cart/view").get_data(as_text=True),
        )
