import sqlite3
import unittest

from werkzeug.security import check_password_hash, generate_password_hash

from app.domain.exceptions import DuplicateEmailError
from app.domain.user import User
from app.infrastructure.user_repository import SQLiteUserRepository


class TestUS01SQLiteUserRepository(unittest.TestCase):
    """US01: testa a persistência SQLite de usuários."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.repository = SQLiteUserRepository(self.connection)
        self.repository.create_table()

    def tearDown(self):
        self.connection.close()

    def test_us01_add_and_get_user_with_password_hash(self):
        """US01: deve persistir usuário sem senha em texto puro."""
        password_hash = generate_password_hash("senha-segura")
        user = User(
            name="Maria Silva",
            email="maria@example.com",
            password_hash=password_hash,
            role="user",
        )

        self.repository.add_user(user)
        stored_user = self.repository.get_user_by_email("MARIA@EXAMPLE.COM")
        stored_password = self.connection.execute(
            """
            SELECT password_hash
            FROM users
            WHERE email = ?;
            """,
            ("maria@example.com",),
        ).fetchone()[0]

        self.assertEqual(stored_user.name, "Maria Silva")
        self.assertEqual(stored_user.email, "maria@example.com")
        self.assertEqual(stored_user.role, "user")
        self.assertNotEqual(stored_password, "senha-segura")
        self.assertTrue(check_password_hash(stored_password, "senha-segura"))

    def test_us01_reject_duplicate_email(self):
        """US01: deve rejeitar e-mail duplicado no SQLite."""
        first_user = User(
            name="Maria Silva",
            email="maria@example.com",
            password_hash=generate_password_hash("senha-segura"),
            role="user",
        )
        duplicate_user = User(
            name="Outra Maria",
            email="MARIA@EXAMPLE.COM",
            password_hash=generate_password_hash("outra-senha"),
            role="user",
        )
        self.repository.add_user(first_user)

        with self.assertRaisesRegex(
            DuplicateEmailError,
            "^Já existe um usuário com o e-mail maria@example.com\\.$",
        ):
            self.repository.add_user(duplicate_user)

        user_count = self.connection.execute("SELECT COUNT(*) FROM users;").fetchone()[
            0
        ]
        self.assertEqual(user_count, 1)
