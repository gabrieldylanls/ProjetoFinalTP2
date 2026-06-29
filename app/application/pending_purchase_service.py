"""Casos de uso de itens não comprados."""

from datetime import datetime, timezone
from typing import Callable

from app.domain.exceptions import (
    InvalidPendingPurchaseItemError,
    PendingPurchaseItemNotFoundError,
    ProductNotFoundError,
    ShoppingListItemNotFoundError,
    ShoppingListNotFoundError,
)
from app.domain.pending_purchase_item import PendingPurchaseItem
from app.domain.shopping_list import ShoppingListItem


class PendingPurchaseService:
    """US07: coordena itens pendentes gerados a partir de listas."""

    def __init__(
        self,
        pending_repository,
        shopping_list_repository,
        product_repository,
        price_repository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """US07: inicializa o serviço.

        Pré-condição: repositórios devem oferecer as operações esperadas.
        Pós-condição: o serviço fica pronto para gerenciar pendências.
        """
        self.pending_repository = pending_repository
        self.shopping_list_repository = shopping_list_repository
        self.product_repository = product_repository
        self.price_repository = price_repository
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def mark_item_as_pending(
        self,
        user_id: int,
        list_id: int,
        bar_code: str,
        quantity: int,
    ) -> PendingPurchaseItem:
        """US07: move total ou parte de um item de lista para pendentes.

        Pré-condição: a lista é própria, o item existe e quantity é válida.
        Pós-condição: item pendente é criado/somado e a lista perde a quantidade.
        """
        self._ensure_owned_list(user_id, list_id)
        item = self._get_list_item_or_raise(list_id, bar_code)
        PendingPurchaseItem(
            user_id=user_id,
            bar_code=bar_code,
            quantity=quantity,
            source_list_id=list_id,
            created_at=self.clock(),
        )
        if quantity > item.quantity:
            raise InvalidPendingPurchaseItemError(
                "A quantidade pendente não pode ser maior que a quantidade da lista."
            )

        pending_item = self.pending_repository.upsert_item(
            PendingPurchaseItem(
                user_id=user_id,
                bar_code=bar_code,
                quantity=quantity,
                source_list_id=list_id,
                created_at=self.clock(),
            )
        )

        if quantity == item.quantity:
            self.shopping_list_repository.remove_item(list_id, bar_code)
        else:
            self.shopping_list_repository.update_item(
                ShoppingListItem(
                    list_id=list_id,
                    bar_code=bar_code,
                    quantity=item.quantity - quantity,
                )
            )
        return pending_item

    def list_pending_items(self, user_id: int) -> list[tuple]:
        """US07: lista pendências com produto e menor preço observado."""
        details = []
        for item in self.pending_repository.list_items(user_id):
            product_with_quantity = self.product_repository.get_product_by_bar_code(
                item.bar_code
            )
            if product_with_quantity is None:
                raise ProductNotFoundError(
                    f"Produto com o código de barras {item.bar_code} não encontrado."
                )
            product, _ = product_with_quantity
            details.append(
                (
                    item,
                    product,
                    self.price_repository.find_lowest_price_by_product(item.bar_code),
                )
            )
        return details

    def update_pending_quantity(
        self,
        user_id: int,
        bar_code: str,
        quantity: int,
    ) -> PendingPurchaseItem:
        """US07: altera a quantidade de um item pendente próprio."""
        item = self._get_pending_or_raise(user_id, bar_code)
        updated = PendingPurchaseItem(
            user_id=item.user_id,
            bar_code=item.bar_code,
            quantity=quantity,
            source_list_id=item.source_list_id,
            created_at=item.created_at,
        )
        self.pending_repository.update_quantity(user_id, bar_code, updated.quantity)
        return updated

    def resolve_pending_item(self, user_id: int, bar_code: str) -> None:
        """US07: remove um item pendente próprio."""
        self._get_pending_or_raise(user_id, bar_code)
        self.pending_repository.remove_item(user_id, bar_code)

    def _ensure_owned_list(self, user_id: int, list_id: int) -> None:
        """US07: garante que a lista pertença ao usuário."""
        shopping_list = self.shopping_list_repository.get_shopping_list_by_id(list_id)
        if shopping_list is None or shopping_list.user_id != user_id:
            raise ShoppingListNotFoundError(
                f"Lista de compras {list_id} não encontrada."
            )

    def _get_list_item_or_raise(
        self,
        list_id: int,
        bar_code: str,
    ) -> ShoppingListItem:
        """US07: retorna um item de lista ou informa ausência."""
        item = self.shopping_list_repository.get_item(list_id, bar_code)
        if item is None:
            raise ShoppingListItemNotFoundError(
                "Item não encontrado na lista de compras."
            )
        return item

    def _get_pending_or_raise(
        self,
        user_id: int,
        bar_code: str,
    ) -> PendingPurchaseItem:
        """US07: retorna uma pendência própria ou informa ausência."""
        item = self.pending_repository.get_item(user_id, bar_code)
        if item is None:
            raise PendingPurchaseItemNotFoundError(
                "Item pendente não encontrado."
            )
        return item
