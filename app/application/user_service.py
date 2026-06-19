"""Casos de uso relacionados a usuários."""

from werkzeug.security import check_password_hash, generate_password_hash

from app.domain.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidUserError,
)
from app.domain.user import User


class UserService:
    """US01: coordena o cadastro seguro de usuários."""

    def __init__(self, user_repository) -> None:
        """Inicializa o serviço de usuários.

        Pré-condição: user_repository deve implementar busca e inclusão.
        Pós-condição: o serviço fica pronto para cadastrar usuários.
        """
        self.user_repository = user_repository

    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        role: str = "user",
    ) -> User:
        """US01: cria e persiste um usuário com senha protegida.

        Pré-condição: os dados devem ser válidos e o e-mail deve ser único.
        Pós-condição: retorna o usuário salvo sem armazenar a senha original.
        """
        self._validate_password(password)
        password_hash = generate_password_hash(password)
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
        )

        if self.user_repository.get_user_by_email(user.email) is not None:
            raise DuplicateEmailError(
                f"Já existe um usuário com o e-mail {user.email}."
            )

        self.user_repository.add_user(user)
        return user

    def authenticate_user(self, email: str, password: str) -> User:
        """US01: autentica usuário por e-mail e senha.

        Pré-condição: email e password devem ser as credenciais informadas.
        Pós-condição: retorna o usuário ou lança InvalidCredentialsError.
        """
        if not isinstance(email, str) or not isinstance(password, str):
            raise InvalidCredentialsError("E-mail ou senha inválidos.")

        user = self.user_repository.get_user_by_email(email.strip().lower())
        if user is None or not check_password_hash(
            user.password_hash,
            password,
        ):
            raise InvalidCredentialsError("E-mail ou senha inválidos.")

        return user

    @staticmethod
    def _validate_password(password: str) -> None:
        """US01: valida a senha recebida antes de gerar o hash."""
        if not isinstance(password, str) or not password:
            raise InvalidUserError("A senha do usuário não pode estar vazia.")
