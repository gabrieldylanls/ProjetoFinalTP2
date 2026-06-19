"""Regras de validação da quantidade em estoque."""

from app.domain.exceptions import InvalidQuantityError


def validate_quantity(quantity: object) -> None:
    """Valida uma quantidade de estoque.

    Pré-condição: quantity deve ser um inteiro maior ou igual a zero.
    Pós-condição: retorna sem efeito ou lança InvalidQuantityError.
    """
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise InvalidQuantityError(
            "A quantidade do produto deve ser um número inteiro."
        )
    if quantity < 0:
        raise InvalidQuantityError("A quantidade do produto não pode ser negativa.")
