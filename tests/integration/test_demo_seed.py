import sqlite3
import unittest

from werkzeug.security import check_password_hash

from app.infrastructure.demo_seed import seed_demo_data


class TestDEMODemoSeed(unittest.TestCase):
    """DEMO: testa a população idempotente do banco de demonstração."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")

    def tearDown(self):
        self.connection.close()

    def test_demo_seed_creates_users_and_multiple_products(self):
        """DEMO: carga deve criar acessos e vários produtos fictícios."""
        result = seed_demo_data(self.connection)

        product_count = self.connection.execute(
            "SELECT COUNT(*) FROM products;"
        ).fetchone()[0]
        users = self.connection.execute(
            """
            SELECT email, password_hash, role
            FROM users
            ORDER BY email;
            """
        ).fetchall()

        self.assertGreaterEqual(product_count, 10)
        self.assertEqual(len(users), 2)
        self.assertEqual(
            {user[0] for user in users},
            {"admin@example.com", "usuario@example.com"},
        )
        self.assertEqual(
            {user[2] for user in users},
            {"admin", "user"},
        )
        self.assertTrue(
            check_password_hash(
                next(user[1] for user in users if user[0] == "admin@example.com"),
                "admin123",
            )
        )
        self.assertEqual(result["products_created"], product_count)
        self.assertEqual(result["users_created"], 2)

    def test_demo_seed_is_idempotent(self):
        """DEMO: executar a carga novamente não deve duplicar registros."""
        first_result = seed_demo_data(self.connection)
        second_result = seed_demo_data(self.connection)

        product_count = self.connection.execute(
            "SELECT COUNT(*) FROM products;"
        ).fetchone()[0]
        user_count = self.connection.execute("SELECT COUNT(*) FROM users;").fetchone()[
            0
        ]

        self.assertGreater(first_result["products_created"], 0)
        self.assertEqual(first_result["users_created"], 2)
        self.assertEqual(second_result["products_created"], 0)
        self.assertEqual(second_result["users_created"], 0)
        self.assertGreaterEqual(product_count, 10)
        self.assertEqual(user_count, 2)
