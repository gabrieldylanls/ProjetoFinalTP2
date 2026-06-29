"""Entidade de itens pendentes de compra."""

from datetime import datetime

from app.domain.exceptions import InvalidPendingPurchaseItemError


class PendingPurchaseItem:
    """US07: representa um produto não comprado que ficou pendente."""

    def __init__(
        self,
        user_id: int,
        bar_code: str,
        quantity: int,
        source_list_id: int | None,
        created_at: datetime,
    ) -> None:
        """US07: cria um item pendente validado.

        Pré-condição: usuário, produto, quantidade e data devem ser válidos.
        Pós-condição: o item é criado ou InvalidPendingPurchaseItemError é lançada.
        """
        self.user_id = self._validate_int(user_id, "usuário")
        self.bar_code = self._validate_bar_code(bar_code)
        self.quantity = self._validate_quantity(quantity)
        self.source_list_id = self._validate_optional_int(source_list_id)
        self.created_at = self._validate_created_at(created_at)

    @staticmethod
    def _validate_int(value: int, label: str) -> int:
        """US07: valida um identificador obrigatório."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidPendingPurchaseItemError(
                f"O identificador do {label} deve ser um número inteiro."
            )
        return value

    @staticmethod
    def _validate_optional_int(value: int | None) -> int | None:
        """US07: valida o identificador opcional da lista de origem."""
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidPendingPurchaseItemError(
                "O identificador da lista de origem deve ser um número inteiro."
            )
        return value

    @staticmethod
    def _validate_bar_code(value: str) -> str:
        """US07: valida o código de barras do item pendente."""
        if not isinstance(value, str) or not value:
            raise InvalidPendingPurchaseItemError(
                "O código de barras do item pendente não pode estar vazio."
            )
        return value

    @staticmethod
    def _validate_quantity(value: int) -> int:
        """US07: valida a quantidade pendente."""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise InvalidPendingPurchaseItemError(
                "A quantidade pendente deve ser maior que zero."
            )
        return value

    @staticmethod
    def _validate_created_at(value: datetime) -> datetime:
        """US07: valida a data de criação."""
        if not isinstance(value, datetime):
            raise InvalidPendingPurchaseItemError(
                "A data do item pendente deve ser válida."
            )
        return value
