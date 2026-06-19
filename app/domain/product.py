"""Entidades e regras de validação de produtos."""

import math

from app.domain.exceptions import InvalidProductError


class Product:
    """Representa um produto com atributos sempre válidos."""

    BAR_CODE_LENGTH = 13

    def __init__(
        self,
        name: str,
        brand: str,
        price: int | float,
        bar_code: str,
    ) -> None:
        """Cria um produto.

        Pré-condição: os argumentos devem atender às regras dos atributos.
        Pós-condição: o produto é criado ou InvalidProductError é lançada.
        """
        self.name = name
        self.brand = brand
        self.price = price
        self.bar_code = bar_code

    @property
    def name(self) -> str:
        """Retorna o nome válido armazenado."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Atualiza o nome.

        Pré-condição: value deve ser uma string não vazia.
        Pós-condição: o nome é atualizado ou InvalidProductError é lançada.
        """
        self._validate_text(
            value=value,
            field_label="nome",
            article="O",
            empty_adjective="vazio",
        )
        self._name = value

    @property
    def brand(self) -> str:
        """Retorna a marca válida armazenada."""
        return self._brand

    @brand.setter
    def brand(self, value: str) -> None:
        """Atualiza a marca.

        Pré-condição: value deve ser uma string não vazia.
        Pós-condição: a marca é atualizada ou InvalidProductError é lançada.
        """
        self._validate_text(
            value=value,
            field_label="marca",
            article="A",
            empty_adjective="vazia",
        )
        self._brand = value

    @property
    def price(self) -> int | float:
        """Retorna o preço válido armazenado."""
        return self._price

    @price.setter
    def price(self, value: int | float) -> None:
        """Atualiza o preço.

        Pré-condição: value deve ser numérico, finito e não negativo.
        Pós-condição: o preço é atualizado ou InvalidProductError é lançada.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidProductError("O preço do produto deve ser um número.")
        if isinstance(value, float) and not math.isfinite(value):
            raise InvalidProductError("O preço do produto deve ser finito.")
        if value < 0:
            raise InvalidProductError("O preço do produto não pode ser negativo.")
        self._price = value

    @property
    def bar_code(self) -> str:
        """Retorna o código de barras válido armazenado."""
        return self._bar_code

    @bar_code.setter
    def bar_code(self, value: str) -> None:
        """Atualiza o código de barras.

        Pré-condição: value deve conter exatamente 13 dígitos ASCII.
        Pós-condição: o código é atualizado ou InvalidProductError é lançada.
        """
        if not isinstance(value, str):
            raise InvalidProductError("O código de barras deve ser uma string.")
        if (
            len(value) != self.BAR_CODE_LENGTH
            or not value.isascii()
            or not value.isdigit()
        ):
            raise InvalidProductError(
                "O código de barras deve conter exatamente 13 dígitos ASCII."
            )
        self._bar_code = value

    @staticmethod
    def _validate_text(
        value: str,
        field_label: str,
        article: str,
        empty_adjective: str,
    ) -> None:
        """Valida um campo textual.

        Pré-condição: os argumentos devem descrever o campo recebido.
        Pós-condição: retorna sem efeito ou lança InvalidProductError.
        """
        if not isinstance(value, str):
            raise InvalidProductError(
                f"{article} {field_label} do produto deve ser uma string."
            )
        if not value.strip():
            raise InvalidProductError(
                f"{article} {field_label} do produto não pode estar {empty_adjective}."
            )
