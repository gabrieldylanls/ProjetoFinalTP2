"""Entidade de sugestões de produtos."""

from datetime import datetime

from app.domain.exceptions import InvalidProductSuggestionError
from app.domain.product import Product
from app.domain.quantity import validate_quantity


class ProductSuggestion:
    """AD05: representa uma sugestão de produto aguardando revisão."""

    VALID_STATUSES = {"pending", "approved", "rejected"}

    def __init__(
        self,
        suggestion_id: int | None,
        user_id: int,
        name: str,
        brand: str,
        price: int | float,
        bar_code: str,
        quantity: int,
        status: str,
        created_at: datetime,
        reviewed_at: datetime | None = None,
        reviewer_id: int | None = None,
        rejection_reason: str | None = None,
    ) -> None:
        """AD05: cria uma sugestão validada.

        Pré-condição: os dados devem formar um produto válido.
        Pós-condição: a sugestão é criada ou uma exceção é lançada.
        """
        Product(name=name, brand=brand, price=price, bar_code=bar_code)
        validate_quantity(quantity)
        self.suggestion_id = self._validate_optional_int(
            suggestion_id,
            "sugestão",
        )
        self.user_id = self._validate_int(user_id, "usuário")
        self.name = name
        self.brand = brand
        self.price = price
        self.bar_code = bar_code
        self.quantity = quantity
        self.status = self._validate_status(status)
        self.created_at = self._validate_datetime(created_at, "criação")
        self.reviewed_at = self._validate_optional_datetime(reviewed_at)
        self.reviewer_id = self._validate_optional_int(reviewer_id, "revisor")
        self.rejection_reason = self._normalize_reason(rejection_reason)

    @staticmethod
    def _validate_int(value: int, label: str) -> int:
        """AD05: valida um identificador obrigatório."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidProductSuggestionError(
                f"O identificador do {label} deve ser um número inteiro."
            )
        return value

    @staticmethod
    def _validate_optional_int(value: int | None, label: str) -> int | None:
        """AD05: valida um identificador opcional."""
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidProductSuggestionError(
                f"O identificador da {label} deve ser um número inteiro."
            )
        return value

    @classmethod
    def _validate_status(cls, value: str) -> str:
        """AD05: valida o estado da revisão."""
        if value not in cls.VALID_STATUSES:
            raise InvalidProductSuggestionError("O status da sugestão é inválido.")
        return value

    @staticmethod
    def _validate_datetime(value: datetime, label: str) -> datetime:
        """AD05: valida uma data obrigatória."""
        if not isinstance(value, datetime):
            raise InvalidProductSuggestionError(f"A data de {label} deve ser válida.")
        return value

    @staticmethod
    def _validate_optional_datetime(value: datetime | None) -> datetime | None:
        """AD05: valida uma data opcional."""
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise InvalidProductSuggestionError("A data de revisão deve ser válida.")
        return value

    @staticmethod
    def _normalize_reason(value: str | None) -> str | None:
        """AD05: normaliza a justificativa de rejeição."""
        if value is None:
            return None
        if not isinstance(value, str):
            raise InvalidProductSuggestionError(
                "A justificativa de rejeição deve ser uma string."
            )
        normalized = value.strip()
        return normalized or None
