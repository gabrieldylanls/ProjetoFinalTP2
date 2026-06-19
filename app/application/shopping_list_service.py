"""Casos de uso relacionados a listas de compras."""

from datetime import datetime, timezone
from typing import Callable

from app.domain.exceptions import (
    ProductNotFoundError,
    ShoppingListItemNotFoundError,
    ShoppingListNotFoundError,
)
from app.domain.shopping_list import ShoppingList, ShoppingListItem


class ShoppingListService:
    """US03: coordena listas de compras e seus itens."""

    def __init__(
        self,
        shopping_list_repository,
        clock: Callable[[], datetime] | None = None,
        product_repository=None,
    ) -> None:
        """US03: inicializa o serviço de listas de compras.

        Pré-condição: os repositórios devem implementar suas operações.
        Pós-condição: o serviço fica pronto para gerenciar listas e itens.
        """
        self.shopping_list_repository = shopping_list_repository
        self.product_repository = product_repository
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def create_shopping_list(
        self,
        user_id: int,
        name: str,
    ) -> ShoppingList:
        """US03: cria uma lista associada ao usuário autenticado.

        Pré-condição: user_id e name devem ser válidos.
        Pós-condição: retorna a lista criada e persistida.
        """
        shopping_list = ShoppingList(
            list_id=None,
            user_id=user_id,
            name=name,
            created_at=self.clock(),
        )
        self.shopping_list_repository.add_shopping_list(shopping_list)
        return shopping_list

    def add_item(
        self,
        user_id: int,
        list_id: int,
        bar_code: str,
        quantity: int,
    ) -> ShoppingListItem:
        """US03: adiciona um produto existente à lista do usuário.

        Pré-condição: lista própria, produto existente e quantidade positiva.
        Pós-condição: retorna o item persistido na lista.
        """
        self._get_owned_list_or_raise(user_id, list_id)
        self._get_product_or_raise(bar_code)
        item = ShoppingListItem(list_id, bar_code, quantity)
        self.shopping_list_repository.add_item(item)
        return item

    def update_item(
        self,
        user_id: int,
        list_id: int,
        bar_code: str,
        quantity: int,
    ) -> ShoppingListItem:
        """US03: altera a quantidade de um item da lista do usuário.

        Pré-condição: lista própria, item existente e quantidade positiva.
        Pós-condição: retorna o item com quantidade persistida.
        """
        self._get_owned_list_or_raise(user_id, list_id)
        self._get_item_or_raise(list_id, bar_code)
        item = ShoppingListItem(list_id, bar_code, quantity)
        self.shopping_list_repository.update_item(item)
        return item

    def remove_item(
        self,
        user_id: int,
        list_id: int,
        bar_code: str,
    ) -> None:
        """US03: remove um item existente da lista do usuário.

        Pré-condição: a lista deve pertencer ao usuário e conter o item.
        Pós-condição: o item deixa de existir na lista.
        """
        self._get_owned_list_or_raise(user_id, list_id)
        self._get_item_or_raise(list_id, bar_code)
        self.shopping_list_repository.remove_item(list_id, bar_code)

    def _get_owned_list_or_raise(
        self,
        user_id: int,
        list_id: int,
    ) -> ShoppingList:
        """US03: retorna a lista quando ela pertence ao usuário."""
        shopping_list = self.shopping_list_repository.get_shopping_list_by_id(list_id)
        if shopping_list is None or shopping_list.user_id != user_id:
            raise ShoppingListNotFoundError(
                f"Lista de compras {list_id} não encontrada."
            )
        return shopping_list

    def _get_product_or_raise(self, bar_code: str):
        """US03: retorna o produto ou informa que ele não existe."""
        product = self.product_repository.get_product_by_bar_code(bar_code)
        if product is None:
            raise ProductNotFoundError(
                f"Produto com o código de barras {bar_code} não encontrado."
            )
        return product

    def _get_item_or_raise(
        self,
        list_id: int,
        bar_code: str,
    ) -> ShoppingListItem:
        """US03: retorna o item ou informa que ele não existe."""
        item = self.shopping_list_repository.get_item(list_id, bar_code)
        if item is None:
            raise ShoppingListItemNotFoundError(
                "Item não encontrado na lista de compras."
            )
        return item
