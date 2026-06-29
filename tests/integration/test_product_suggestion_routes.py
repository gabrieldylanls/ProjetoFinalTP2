import sqlite3
import unittest

from app.web.app import create_app


class TestAD05ProductSuggestionRoutes(unittest.TestCase):
    """AD05: testa sugestão e aprovação administrativa de produtos."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()

    def tearDown(self):
        self.connection.close()

    def authenticate(self, user_id=7, role="user"):
        """AD05: configura sessão do usuário informado."""
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
            flask_session["user_id"] = user_id
            flask_session["role"] = role

    def suggestion_payload(self, bar_code="1234567890888"):
        """AD05: retorna uma sugestão válida."""
        return {
            "name": "Macarrão",
            "brand": "Renata",
            "price": 6.50,
            "bar_code": bar_code,
            "quantity": 12,
        }

    def create_suggestion(self):
        """AD05: cria uma sugestão como usuário comum."""
        self.authenticate(user_id=7, role="user")
        return self.client.post(
            "/product-suggestions",
            json=self.suggestion_payload(),
        )

    def test_ad05_authenticated_user_creates_suggestion(self):
        """AD05: usuário autenticado deve sugerir produto."""
        self.authenticate(user_id=7, role="user")

        response = self.client.post(
            "/product-suggestions",
            json=self.suggestion_payload(),
        )

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["user_id"], 7)

    def test_ad05_reject_existing_catalog_product(self):
        """AD05: sugestão com código cadastrado deve retornar conflito."""
        self.authenticate(user_id=1, role="admin")
        self.client.post(
            "/products",
            json={
                "name": "Produto existente",
                "brand": "Marca",
                "price": 1.0,
                "bar_code": "1234567890888",
                "quantity": 1,
            },
        )
        self.authenticate(user_id=7, role="user")

        response = self.client.post(
            "/product-suggestions",
            json=self.suggestion_payload(),
        )

        self.assertEqual(response.status_code, 409)

    def test_ad05_reject_visitor_suggestion(self):
        """AD05: visitante não deve criar sugestão."""
        response = self.client.post(
            "/product-suggestions",
            json=self.suggestion_payload(),
        )

        self.assertEqual(response.status_code, 401)

    def test_ad05_admin_lists_pending_suggestions(self):
        """AD05: admin deve listar sugestões pendentes."""
        self.create_suggestion()
        self.authenticate(user_id=1, role="admin")

        response = self.client.get("/admin/product-suggestions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)
        self.assertEqual(response.get_json()[0]["name"], "Macarrão")

    def test_ad05_common_user_cannot_access_admin_queue(self):
        """AD05: usuário comum não acessa fila administrativa."""
        self.authenticate(user_id=7, role="user")

        response = self.client.get("/admin/product-suggestions")

        self.assertEqual(response.status_code, 403)

    def test_ad05_admin_approves_suggestion_and_product_appears(self):
        """AD05: aprovação cria produto ativo no catálogo."""
        suggestion_id = self.create_suggestion().get_json()["id"]
        self.authenticate(user_id=1, role="admin")

        response = self.client.post(
            f"/admin/product-suggestions/{suggestion_id}/approve"
        )
        search_response = self.client.get("/products?q=macarrão")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "approved")
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.get_json()[0]["bar_code"], "1234567890888")

    def test_ad05_admin_rejects_suggestion(self):
        """AD05: rejeição remove sugestão da fila pendente."""
        suggestion_id = self.create_suggestion().get_json()["id"]
        self.authenticate(user_id=1, role="admin")

        response = self.client.post(
            f"/admin/product-suggestions/{suggestion_id}/reject",
            json={"rejection_reason": "Produto duplicado em análise."},
        )
        pending_response = self.client.get("/admin/product-suggestions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "rejected")
        self.assertEqual(pending_response.get_json(), [])

    def test_ad05_approve_conflicts_when_product_was_created_later(self):
        """AD05: aprovação deve falhar se código virou duplicado."""
        suggestion_id = self.create_suggestion().get_json()["id"]
        self.authenticate(user_id=1, role="admin")
        self.client.post(
            "/products",
            json={
                "name": "Produto existente",
                "brand": "Marca",
                "price": 1.0,
                "bar_code": "1234567890888",
                "quantity": 1,
            },
        )

        response = self.client.post(
            f"/admin/product-suggestions/{suggestion_id}/approve"
        )

        self.assertEqual(response.status_code, 409)
