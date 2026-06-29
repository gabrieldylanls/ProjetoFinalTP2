"""Casos de uso de sugestões de produtos."""

from datetime import datetime, timezone
from typing import Callable

from app.domain.exceptions import (
    ProductSuggestionConflictError,
    ProductSuggestionNotFoundError,
)
from app.domain.product_suggestion import ProductSuggestion


class ProductSuggestionService:
    """AD05: coordena sugestão e revisão administrativa de produtos."""

    def __init__(
        self,
        suggestion_repository,
        product_service,
        product_repository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """AD05: inicializa o serviço de sugestões."""
        self.suggestion_repository = suggestion_repository
        self.product_service = product_service
        self.product_repository = product_repository
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def suggest_product(
        self,
        user_id: int,
        name: str,
        brand: str,
        price: int | float,
        bar_code: str,
        quantity: int,
    ) -> ProductSuggestion:
        """AD05: registra sugestão de produto feita por usuário autenticado."""
        if self.product_repository.get_product_by_bar_code(bar_code) is not None:
            raise ProductSuggestionConflictError(
                f"Já existe um produto com o código de barras {bar_code}."
            )
        suggestion = ProductSuggestion(
            suggestion_id=None,
            user_id=user_id,
            name=name,
            brand=brand,
            price=price,
            bar_code=bar_code,
            quantity=quantity,
            status="pending",
            created_at=self.clock(),
        )
        self.suggestion_repository.add_suggestion(suggestion)
        return suggestion

    def list_pending_suggestions(self) -> list[ProductSuggestion]:
        """AD05: lista sugestões pendentes para revisão administrativa."""
        return self.suggestion_repository.list_pending_suggestions()

    def approve_suggestion(
        self,
        suggestion_id: int,
        reviewer_id: int,
    ) -> ProductSuggestion:
        """AD05: aprova uma sugestão e cria o produto no catálogo."""
        suggestion = self._get_pending_or_raise(suggestion_id)
        if self.product_repository.get_product_by_bar_code(
            suggestion.bar_code
        ) is not None:
            raise ProductSuggestionConflictError(
                f"Já existe um produto com o código de barras {suggestion.bar_code}."
            )
        self.product_service.create_product(
            name=suggestion.name,
            brand=suggestion.brand,
            price=suggestion.price,
            bar_code=suggestion.bar_code,
            quantity=suggestion.quantity,
        )
        reviewed = ProductSuggestion(
            suggestion_id=suggestion.suggestion_id,
            user_id=suggestion.user_id,
            name=suggestion.name,
            brand=suggestion.brand,
            price=suggestion.price,
            bar_code=suggestion.bar_code,
            quantity=suggestion.quantity,
            status="approved",
            created_at=suggestion.created_at,
            reviewed_at=self.clock(),
            reviewer_id=reviewer_id,
            rejection_reason=None,
        )
        self.suggestion_repository.update_review(reviewed)
        return reviewed

    def reject_suggestion(
        self,
        suggestion_id: int,
        reviewer_id: int,
        rejection_reason: str | None = None,
    ) -> ProductSuggestion:
        """AD05: rejeita uma sugestão de produto pendente."""
        suggestion = self._get_pending_or_raise(suggestion_id)
        reviewed = ProductSuggestion(
            suggestion_id=suggestion.suggestion_id,
            user_id=suggestion.user_id,
            name=suggestion.name,
            brand=suggestion.brand,
            price=suggestion.price,
            bar_code=suggestion.bar_code,
            quantity=suggestion.quantity,
            status="rejected",
            created_at=suggestion.created_at,
            reviewed_at=self.clock(),
            reviewer_id=reviewer_id,
            rejection_reason=rejection_reason,
        )
        self.suggestion_repository.update_review(reviewed)
        return reviewed

    def _get_pending_or_raise(self, suggestion_id: int) -> ProductSuggestion:
        """AD05: retorna uma sugestão pendente ou informa ausência."""
        suggestion = self.suggestion_repository.get_suggestion_by_id(suggestion_id)
        if suggestion is None or suggestion.status != "pending":
            raise ProductSuggestionNotFoundError(
                f"Sugestão de produto {suggestion_id} não encontrada."
            )
        return suggestion
