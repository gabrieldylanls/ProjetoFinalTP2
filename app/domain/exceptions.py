class InvalidProductError(Exception):
    """Custom exception for invalid product attributes."""
    def __init__(self, message):
        super().__init__(message)

class DuplicateBarcodeError(Exception):
    """Custom exception for duplicate bar code errors."""
    def __init__(self, message):
        super().__init__(message)

class ProductNotFoundError(Exception):
    """Custom exception for product not found errors."""
    def __init__(self, message):
        super().__init__(message)