import sqlite3
import unittest

from app.web.app import create_app


class TestAD04AdminMetricsRoutes(unittest.TestCase):
    """AD04: testa consulta protegida das métricas administrativas."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()

    def tearDown(self):
        self.connection.close()

    def authenticate_as(self, role, user_id=1):
        """AD04: configura uma sessão autenticada para o teste."""
        with self.client.session_transaction() as flask_session:
            flask_session.clear()
            flask_session["user_id"] = user_id
            flask_session["role"] = role

    def test_ad04_admin_gets_metrics_from_sqlite(self):
        """AD04: admin deve receber métricas persistidas com HTTP 200."""
        self.connection.execute(
            """
            INSERT INTO products (
                bar_code, name, brand, price, quantity, active
            )
            VALUES ('1234567890123', 'Arroz', 'Marca A', 10.0, 5, 1);
            """
        )
        self.connection.execute(
            """
            INSERT INTO users (email, name, password_hash, role)
            VALUES ('user@example.com', 'Usuário', 'hash', 'user');
            """
        )
        self.connection.execute(
            """
            INSERT INTO shopping_lists (user_id, name, created_at)
            VALUES (1, 'Lista A', '2026-06-19T10:00:00');
            """
        )
        self.connection.execute(
            """
            INSERT INTO product_prices (
                product_bar_code, store_id, user_id, price, created_at
            )
            VALUES ('1234567890123', 1, 1, 9.50, '2026-06-19T10:00:00');
            """
        )
        self.connection.commit()
        self.authenticate_as("admin")

        response = self.client.get("/admin/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "total_products": 1,
                "total_users": 1,
                "total_shopping_lists": 1,
                "total_registered_prices": 1,
            },
        )

    def test_ad04_common_user_cannot_get_metrics(self):
        """AD04: usuário comum deve receber HTTP 403."""
        self.authenticate_as("user")

        response = self.client.get("/admin/metrics")

        self.assertEqual(response.status_code, 403)

    def test_ad04_unauthenticated_user_cannot_get_metrics(self):
        """AD04: visitante deve receber HTTP 401."""
        response = self.client.get("/admin/metrics")

        self.assertEqual(response.status_code, 401)
