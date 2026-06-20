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

    def test_us01_web_login_page(self):
        """US01/WEB: tela de login deve responder 200 e exibir formulário."""
        response = self.client.get("/login")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Entrar", html)
        self.assertIn('name="email"', html)
        self.assertIn('name="password"', html)

    def test_us01_web_login_valid_user_redirects_to_catalog(self):
        """US01/WEB: credenciais válidas devem criar sessão e redirecionar."""
        self.client.post(
            "/auth/register",
            json={
                "name": "Maria Silva",
                "email": "maria@example.com",
                "password": "senha-segura",
            },
        )

        response = self.client.post(
            "/login",
            data={
                "email": "maria@example.com",
                "password": "senha-segura",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/catalog"))
        with self.client.session_transaction() as flask_session:
            self.assertIsInstance(flask_session["user_id"], int)
            self.assertEqual(flask_session["role"], "user")

    def test_us01_web_admin_login_redirects_to_dashboard(self):
        """US01/WEB: administrador deve entrar no painel administrativo."""
        self.connection.execute(
            """
            INSERT INTO users (email, name, password_hash, role)
            VALUES (
                'admin@example.com',
                'Administrador',
                'scrypt:32768:8:1$test$invalid',
                'admin'
            );
            """
        )
        self.connection.commit()
        from werkzeug.security import generate_password_hash

        self.connection.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE email = 'admin@example.com';
            """,
            (generate_password_hash("admin123"),),
        )
        self.connection.commit()

        response = self.client.post(
            "/login",
            data={
                "email": "admin@example.com",
                "password": "admin123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/admin/dashboard"))

    def test_us01_web_login_invalid_credentials_returns_html(self):
        """US01/WEB: credenciais inválidas devem manter a tela com HTTP 401."""
        response = self.client.post(
            "/login",
            data={
                "email": "inexistente@example.com",
                "password": "senha-incorreta",
            },
        )

        self.assertEqual(response.status_code, 401)
        html = response.get_data(as_text=True)
        self.assertIn("E-mail ou senha inválidos.", html)
        self.assertIn("Entrar", html)

    def test_us01_web_logout_clears_session(self):
        """US01/WEB: logout deve limpar a sessão e redirecionar ao login."""
        response = self.client.post("/logout")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))
        with self.client.session_transaction() as flask_session:
            self.assertNotIn("user_id", flask_session)
            self.assertNotIn("role", flask_session)

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

    def test_web_product_catalog_is_paginated(self):
        """WEB: catálogo grande deve exibir paginação sem listar tudo."""
        rows = [
            (
                f"790{index:010d}",
                f"Produto fictício {index:04d}",
                "Marca Teste",
                10.0,
                5,
            )
            for index in range(1, 56)
        ]
        self.connection.executemany(
            """
            INSERT INTO products (
                bar_code, name, brand, price, quantity
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            rows,
        )
        self.connection.commit()

        first_page = self.client.get("/catalog")
        second_page = self.client.get("/catalog?page=2")

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(second_page.status_code, 200)
        self.assertIn("Página 1 de 2", first_page.get_data(as_text=True))
        self.assertIn("Página 2 de 2", second_page.get_data(as_text=True))

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

    def test_ad04_web_admin_dashboard(self):
        """AD04/WEB: admin deve visualizar métricas no painel HTML."""
        response = self.client.get("/admin/dashboard")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Painel administrativo", html)
        self.assertIn("Produtos cadastrados", html)

    def test_web_common_user_navigation_hides_admin_actions(self):
        """WEB: usuário comum não deve visualizar ações administrativas."""
        with self.client.session_transaction() as flask_session:
            flask_session["role"] = "user"

        response = self.client.get("/")

        html = response.get_data(as_text=True)
        self.assertNotIn("Cadastrar produto", html)
        self.assertNotIn("Painel administrativo", html)
        self.assertIn("Locais de compra", html)

    def test_us06_web_authenticated_user_lists_stores(self):
        """US06/WEB: usuário autenticado deve visualizar locais de compra."""
        self.client.post(
            "/stores",
            json={
                "name": "Mercado Central",
                "address": "Rua Principal, 100",
                "observation": "Aberto todos os dias",
            },
        )
        with self.client.session_transaction() as flask_session:
            flask_session["role"] = "user"

        response = self.client.get("/stores/view")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Locais de compra", html)
        self.assertIn("Mercado Central", html)

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
