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


class StoreNotFoundError(Exception):
    """Indica que o local de compra solicitado não foi encontrado."""


class InvalidProductPriceError(Exception):
    """Indica que um preço observado viola uma pré-condição."""


class InvalidPendingPurchaseItemError(Exception):
    """Indica que um item pendente viola uma pré-condição."""


class PendingPurchaseItemNotFoundError(Exception):
    """Indica que o item pendente solicitado não foi encontrado."""


class InvalidProductSuggestionError(Exception):
    """Indica que uma sugestão de produto viola uma pré-condição."""


class ProductSuggestionNotFoundError(Exception):
    """Indica que a sugestão de produto solicitada não foi encontrada."""


class ProductSuggestionConflictError(Exception):
    """Indica conflito entre sugestão de produto e catálogo."""
