"""Entidade e regras de validação de usuários."""

import re

from app.domain.exceptions import InvalidUserError


class User:
    """US01: representa um usuário com credenciais protegidas."""

    VALID_ROLES = {"user", "admin"}
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str,
        user_id: int | None = None,
    ) -> None:
        """US01: cria um usuário validado.

        Pré-condição: os dados devem ser válidos e a senha já deve estar em hash.
        Pós-condição: o usuário é criado ou InvalidUserError é lançada.
        """
        self.user_id = self._validate_user_id(user_id)
        self.name = self._validate_name(name)
        self.email = self._validate_email(email)
        self.password_hash = self._validate_password_hash(password_hash)
        self.role = self._validate_role(role)

    @staticmethod
    def _validate_user_id(user_id: int | None) -> int | None:
        """US01: valida o identificador persistido do usuário."""
        if user_id is None:
            return None
        if isinstance(user_id, bool) or not isinstance(user_id, int):
            raise InvalidUserError(
                "O identificador do usuário deve ser um número inteiro."
            )
        return user_id

    @staticmethod
    def _validate_name(name: str) -> str:
        """US01: valida e normaliza o nome do usuário."""
        if not isinstance(name, str) or not name.strip():
            raise InvalidUserError("O nome do usuário deve ser uma string não vazia.")
        return name.strip()

    @classmethod
    def _validate_email(cls, email: str) -> str:
        """US01: valida e normaliza o e-mail do usuário."""
        if not isinstance(email, str):
            raise InvalidUserError("O e-mail do usuário deve ser uma string válida.")

        normalized_email = email.strip().lower()
        if not cls.EMAIL_PATTERN.fullmatch(normalized_email):
            raise InvalidUserError("O e-mail do usuário deve ser uma string válida.")
        return normalized_email

    @staticmethod
    def _validate_password_hash(password_hash: str) -> str:
        """US01: valida que a credencial protegida foi informada."""
        if not isinstance(password_hash, str) or not password_hash:
            raise InvalidUserError("O hash da senha do usuário não pode estar vazio.")
        return password_hash

    @classmethod
    def _validate_role(cls, role: str) -> str:
        """US01: valida o papel de acesso do usuário."""
        if role not in cls.VALID_ROLES:
            raise InvalidUserError("O papel do usuário deve ser 'user' ou 'admin'.")
        return role
