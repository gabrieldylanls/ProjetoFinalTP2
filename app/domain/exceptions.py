"""Exceções específicas das regras de domínio."""


class InvalidProductError(Exception):
    """Indica que um atributo viola uma pré-condição do produto."""


class InvalidQuantityError(Exception):
    """Indica que a quantidade informada é inválida."""


class DuplicateBarcodeError(Exception):
    """Indica que o código de barras já está cadastrado."""


class ProductNotFoundError(Exception):
    """Indica que o produto solicitado não foi encontrado."""


class InvalidUserError(Exception):
    """Indica que um atributo viola uma pré-condição do usuário."""


class DuplicateEmailError(Exception):
    """Indica que o e-mail já está cadastrado."""


class InvalidCredentialsError(Exception):
    """Indica que as credenciais de autenticação são inválidas."""


class InvalidShoppingListError(Exception):
    """Indica que uma lista de compras viola uma pré-condição."""


class ShoppingListNotFoundError(Exception):
    """Indica que a lista não existe ou não pertence ao usuário."""


class ShoppingListItemNotFoundError(Exception):
    """Indica que o item solicitado não existe na lista."""


class InvalidCartError(Exception):
    """Indica que um item do carrinho viola uma pré-condição."""


class CartItemNotFoundError(Exception):
    """Indica que o item solicitado não existe no carrinho."""


class InvalidStoreError(Exception):
    """Indica que um local de compra viola uma pré-condição."""
