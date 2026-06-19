import unittest

from werkzeug.security import check_password_hash

from app.application.user_service import UserService
from app.domain.exceptions import DuplicateEmailError


class FakeUserRepository:
    """Simula a persistência de usuários em memória."""

    def __init__(self):
        self.users = {}

    def add_user(self, user):
        self.users[user.email] = user

    def get_user_by_email(self, email):
        return self.users.get(email.lower())


class TestUS01UserService(unittest.TestCase):
    """US01: testa o cadastro seguro de usuários."""

    def setUp(self):
        self.repository = FakeUserRepository()
        self.service = UserService(self.repository)

    def test_us01_create_user_with_password_hash(self):
        """US01: deve cadastrar usuário sem armazenar senha em texto puro."""
        user = self.service.create_user(
            name="Maria Silva",
            email="maria@example.com",
            password="senha-segura",
        )

        self.assertEqual(user.role, "user")
        self.assertNotEqual(user.password_hash, "senha-segura")
        self.assertTrue(check_password_hash(user.password_hash, "senha-segura"))
        self.assertIs(self.repository.users[user.email], user)

    def test_us01_create_admin_user(self):
        """US01: deve permitir cadastro com papel admin."""
        user = self.service.create_user(
            name="Administrador",
            email="admin@example.com",
            password="senha-segura",
            role="admin",
        )

        self.assertEqual(user.role, "admin")

    def test_us01_reject_duplicate_email(self):
        """US01: deve rejeitar e-mail duplicado sem diferenciar caixa."""
        self.service.create_user(
            name="Maria Silva",
            email="maria@example.com",
            password="senha-segura",
        )

        with self.assertRaisesRegex(
            DuplicateEmailError,
            "^Já existe um usuário com o e-mail maria@example.com\\.$",
        ):
            self.service.create_user(
                name="Outra Maria",
                email="MARIA@EXAMPLE.COM",
                password="outra-senha",
            )

        self.assertEqual(len(self.repository.users), 1)
