"""Casos de uso relacionados ao carrinho em sessão."""

import math

from app.application.product_service import ProductService
from app.domain.exceptions import CartItemNotFoundError, InvalidCartError
from app.domain.product import Product


class CartService:
    """US04/US05: gerencia itens e total do carrinho em sessão."""

    def __init__(self, product_service: ProductService) -> None:
        """Inicializa o serviço de carrinho.

        Pré-condição: product_service deve permitir consulta de produtos.
        Pós-condição: o serviço fica pronto para operar dados da sessão.
        """
        self.product_service = product_service

    def add_item(
        self,
        cart: dict[str, int],
        bar_code: str,
        quantity: int,
    ) -> Product:
        """US04: adiciona ou substitui um item no carrinho.

        Pré-condição: produto existente e quantidade maior que zero.
        Pós-condição: o carrinho contém o item e retorna seu produto.
        """
        self._validate_quantity(quantity)
        product, _ = self.product_service.get_product(bar_code)
        cart[bar_code] = quantity
        return product

    def update_item(
        self,
        cart: dict[str, int],
        bar_code: str,
        quantity: int,
    ) -> Product:
        """US04: altera a quantidade de um item existente.

        Pré-condição: item existente e quantidade maior que zero.
        Pós-condição: o carrinho contém a nova quantidade.
        """
        self._validate_quantity(quantity)
        self._ensure_item_exists(cart, bar_code)
        product, _ = self.product_service.get_product(bar_code)
        cart[bar_code] = quantity
        return product

    def remove_item(
        self,
        cart: dict[str, int],
        bar_code: str,
    ) -> None:
        """US04: remove um item existente do carrinho.

        Pré-condição: bar_code deve existir no carrinho.
        Pós-condição: o item deixa de existir no carrinho.
        """
        self._ensure_item_exists(cart, bar_code)
        del cart[bar_code]

    def get_items(
        self,
        cart: dict[str, int],
    ) -> list[tuple[Product, int]]:
        """US04: retorna os produtos e quantidades atuais do carrinho.

        Pré-condição: cart deve mapear códigos para quantidades.
        Pós-condição: retorna os itens resolvidos pelo catálogo.
        """
        items = []
        for bar_code, quantity in cart.items():
            product, _ = self.product_service.get_product(bar_code)
            items.append((product, quantity))
        return items

    @staticmethod
    def calculate_total(items: list[tuple[Product, int]]) -> int | float:
        """US05: calcula o total estimado dos itens do carrinho.

        Pré-condição: cada item deve possuir preço válido e quantidade.
        Pós-condição: retorna a soma de preço vezes quantidade.
        """
        total = 0
        for product, quantity in items:
            price = product.price
            if (
                isinstance(price, bool)
                or not isinstance(price, (int, float))
                or not math.isfinite(price)
                or price < 0
            ):
                raise InvalidCartError("O preço do item do carrinho é inválido.")
            total += price * quantity
        return total

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        """US04: valida uma quantidade estritamente positiva."""
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InvalidCartError("A quantidade do carrinho deve ser maior que zero.")

    @staticmethod
    def _ensure_item_exists(
        cart: dict[str, int],
        bar_code: str,
    ) -> None:
        """US04: garante que o item existe no carrinho."""
        if bar_code not in cart:
            raise CartItemNotFoundError("Item não encontrado no carrinho.")
