"""Casos de uso relacionados a produtos."""

from app.domain.exceptions import DuplicateBarcodeError, ProductNotFoundError
from app.domain.product import Product
from app.domain.quantity import validate_quantity


class ProductService:
    """Coordena regras de aplicação e persistência de produtos."""

    def __init__(self, product_repository) -> None:
        """Inicializa o serviço.

        Pré-condição: o repositório deve implementar busca e inclusão.
        Pós-condição: o serviço fica pronto para executar seus casos de uso.
        """
        self.product_repository = product_repository

    def create_product(
        self,
        name: str,
        brand: str,
        price: int | float,
        bar_code: str,
        quantity: int,
    ) -> Product:
        """Cria e persiste um produto.

        Pré-condição: os dados devem ser válidos e o código deve ser único.
        Pós-condição: retorna o produto salvo ou lança uma exceção.
        """
        validate_quantity(quantity)

        stored_product = self.product_repository.get_product_by_bar_code(bar_code)
        if stored_product is not None:
            raise DuplicateBarcodeError(
                f"Já existe um produto com o código de barras {bar_code}."
            )

        product = Product(
            name=name,
            brand=brand,
            price=price,
            bar_code=bar_code,
        )
        self.product_repository.add_product(product, quantity)
        return product

    def search_products(
        self,
        query: str,
    ) -> list[tuple[Product, int]]:
        """US02: busca produtos por texto parcial no catálogo.

        Pré-condição: query deve conter o texto informado pelo usuário.
        Pós-condição: retorna produtos compatíveis ou lista vazia.
        """
        if not isinstance(query, str) or not query.strip():
            return []

        return self.product_repository.search_products_by_text(query.strip())

    def update_product(
        self,
        bar_code: str,
        name: str,
        brand: str,
        price: int | float,
    ) -> tuple[Product, int]:
        """AD02: edita os dados de um produto existente.

        Pré-condição: o código deve existir e os novos dados devem ser válidos.
        Pós-condição: retorna produto e quantidade com alterações persistidas.
        """
        stored_product = self._get_product_or_raise(bar_code)
        _, quantity = stored_product
        updated_product = Product(
            name=name,
            brand=brand,
            price=price,
            bar_code=bar_code,
        )
        self.product_repository.update_product(updated_product)
        return updated_product, quantity

    def deactivate_product(self, bar_code: str) -> None:
        """AD02: remove logicamente um produto existente.

        Pré-condição: bar_code deve identificar um produto cadastrado.
        Pós-condição: o produto permanece armazenado, marcado como inativo.
        """
        self._get_product_or_raise(bar_code)
        self.product_repository.deactivate_product(bar_code)

    def _get_product_or_raise(
        self,
        bar_code: str,
    ) -> tuple[Product, int]:
        """AD02: retorna o produto ou informa que ele não existe."""
        stored_product = self.product_repository.get_product_by_bar_code(
            bar_code
        )
        if stored_product is None:
            raise ProductNotFoundError(
                f"Produto com o código de barras {bar_code} não encontrado."
            )

        return stored_product
