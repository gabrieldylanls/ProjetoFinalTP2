"""Entidade e regras de validação de listas de compras."""

from datetime import datetime

from app.domain.exceptions import InvalidShoppingListError


class ShoppingList:
    """US03: representa uma lista de compras pertencente a um usuário."""

    def __init__(
        self,
        list_id: int | None,
        user_id: int,
        name: str,
        created_at: datetime,
    ) -> None:
        """US03: cria uma lista de compras validada.

        Pré-condição: usuário, nome e data devem ser válidos.
        Pós-condição: a lista é criada ou InvalidShoppingListError é lançada.
        """
        self.list_id = self._validate_list_id(list_id)
        self.user_id = self._validate_user_id(user_id)
        self.name = self._validate_name(name)
        self.created_at = self._validate_created_at(created_at)

    @staticmethod
    def _validate_list_id(list_id: int | None) -> int | None:
        """US03: valida o identificador opcional da lista."""
        if list_id is None:
            return None
        if isinstance(list_id, bool) or not isinstance(list_id, int):
            raise InvalidShoppingListError(
                "O identificador da lista deve ser um número inteiro."
            )
        return list_id

    @staticmethod
    def _validate_user_id(user_id: int) -> int:
        """US03: valida o identificador do proprietário da lista."""
        if isinstance(user_id, bool) or not isinstance(user_id, int):
            raise InvalidShoppingListError(
                "O identificador do usuário deve ser um número inteiro."
            )
        return user_id

    @staticmethod
    def _validate_name(name: str) -> str:
        """US03: valida e normaliza o nome da lista."""
        if not isinstance(name, str) or not name.strip():
            raise InvalidShoppingListError(
                "O nome da lista de compras não pode estar vazio."
            )
        return name.strip()

    @staticmethod
    def _validate_created_at(created_at: datetime) -> datetime:
        """US03: valida a data de criação da lista."""
        if not isinstance(created_at, datetime):
            raise InvalidShoppingListError(
                "A data de criação da lista deve ser válida."
            )
        return created_at


class ShoppingListItem:
    """US03: representa um produto e sua quantidade em uma lista."""

    def __init__(
        self,
        list_id: int,
        bar_code: str,
        quantity: int,
    ) -> None:
        """US03: cria um item de lista validado.

        Pré-condição: lista, produto e quantidade devem ser válidos.
        Pós-condição: cria o item ou lança InvalidShoppingListError.
        """
        self.list_id = self._validate_list_id(list_id)
        self.bar_code = self._validate_bar_code(bar_code)
        self.quantity = self._validate_quantity(quantity)

    @staticmethod
    def _validate_list_id(list_id: int) -> int:
        """US03: valida o identificador da lista do item."""
        if isinstance(list_id, bool) or not isinstance(list_id, int):
            raise InvalidShoppingListError(
                "O identificador da lista deve ser um número inteiro."
            )
        return list_id

    @staticmethod
    def _validate_bar_code(bar_code: str) -> str:
        """US03: valida o código do produto associado ao item."""
        if not isinstance(bar_code, str) or not bar_code:
            raise InvalidShoppingListError(
                "O código de barras do item não pode estar vazio."
            )
        return bar_code

    @staticmethod
    def _validate_quantity(quantity: int) -> int:
        """US03: valida a quantidade planejada do item."""
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InvalidShoppingListError(
                "A quantidade do item deve ser maior que zero."
            )
        return quantity
