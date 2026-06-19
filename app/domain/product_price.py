"""Entidade e regras do histórico de preços observados."""

import math
from datetime import datetime

from app.domain.exceptions import InvalidProductPriceError


class ProductPrice:
    """US06: representa um preço observado para produto e local."""

    def __init__(
        self,
        product_bar_code: str,
        store_id: int,
        user_id: int,
        price: int | float,
        created_at: datetime,
    ) -> None:
        """US06: cria um registro validado de preço.

        Pré-condição: produto, local, usuário, preço e data devem ser válidos.
        Pós-condição: cria o registro ou lança InvalidProductPriceError.
        """
        self.product_bar_code = self._validate_bar_code(product_bar_code)
        self.store_id = self._validate_identifier(store_id, "local")
        self.user_id = self._validate_identifier(user_id, "usuário")
        self.price = self._validate_price(price)
        self.created_at = self._validate_created_at(created_at)

    @staticmethod
    def _validate_bar_code(product_bar_code: str) -> str:
        """US06: valida o código do produto associado ao preço."""
        if not isinstance(product_bar_code, str) or not product_bar_code:
            raise InvalidProductPriceError(
                "O código de barras do produto não pode estar vazio."
            )
        return product_bar_code

    @staticmethod
    def _validate_identifier(identifier: int, field_name: str) -> int:
        """US06: valida um identificador obrigatório."""
        if (
            isinstance(identifier, bool)
            or not isinstance(identifier, int)
            or identifier <= 0
        ):
            raise InvalidProductPriceError(
                f"O identificador do {field_name} deve ser um inteiro positivo."
            )
        return identifier

    @staticmethod
    def _validate_price(price: int | float) -> int | float:
        """US06: valida um preço observado não negativo e finito."""
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            raise InvalidProductPriceError("O preço observado deve ser um número.")
        if isinstance(price, float) and not math.isfinite(price):
            raise InvalidProductPriceError("O preço observado deve ser finito.")
        if price < 0:
            raise InvalidProductPriceError("O preço observado não pode ser negativo.")
        return price

    @staticmethod
    def _validate_created_at(created_at: datetime) -> datetime:
        """US06: valida a data de criação do registro."""
        if not isinstance(created_at, datetime):
            raise InvalidProductPriceError(
                "A data de registro do preço deve ser válida."
            )
        return created_at
