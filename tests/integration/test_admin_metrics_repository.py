import sqlite3
import unittest

from app.infrastructure.admin_metrics_repository import (
    SQLiteAdminMetricsRepository,
)
from app.web.app import create_app


class TestAD04SQLiteAdminMetricsRepository(unittest.TestCase):
    """AD04: testa contagens administrativas obtidas do SQLite."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        create_app(self.connection)
        self.repository = SQLiteAdminMetricsRepository(self.connection)

    def tearDown(self):
        self.connection.close()

    def test_ad04_get_empty_metrics(self):
        """AD04: banco vazio deve retornar todas as métricas com valor zero."""
        metrics = self.repository.get_metrics()

        self.assertEqual(
            metrics,
            {
                "total_products": 0,
                "total_users": 0,
                "total_shopping_lists": 0,
                "total_registered_prices": 0,
            },
        )

    def test_ad04_count_persisted_records(self):
        """AD04: deve contar registros persistidos nas quatro tabelas."""
        self.connection.execute(
            """
            INSERT INTO products (
                bar_code, name, brand, price, quantity, active
            )
            VALUES
                ('1234567890123', 'Arroz', 'Marca A', 10.0, 5, 1),
                ('1234567890124', 'Feijão', 'Marca B', 8.0, 0, 0);
            """
        )
        self.connection.execute(
            """
            INSERT INTO users (email, name, password_hash, role)
            VALUES
                ('admin@example.com', 'Admin', 'hash-1', 'admin'),
                ('user@example.com', 'Usuário', 'hash-2', 'user');
            """
        )
        self.connection.execute(
            """
            INSERT INTO shopping_lists (user_id, name, created_at)
            VALUES
                (1, 'Lista A', '2026-06-19T10:00:00'),
                (2, 'Lista B', '2026-06-19T11:00:00');
            """
        )
        self.connection.execute(
            """
            INSERT INTO product_prices (
                product_bar_code, store_id, user_id, price, created_at
            )
            VALUES
                ('1234567890123', 1, 2, 9.50, '2026-06-19T10:00:00'),
                ('1234567890123', 1, 2, 9.25, '2026-06-19T11:00:00'),
                ('1234567890124', 1, 1, 7.50, '2026-06-19T12:00:00');
            """
        )
        self.connection.commit()

        metrics = self.repository.get_metrics()

        self.assertEqual(
            metrics,
            {
                "total_products": 2,
                "total_users": 2,
                "total_shopping_lists": 2,
                "total_registered_prices": 3,
            },
        )
