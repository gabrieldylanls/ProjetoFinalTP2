class InvalidProductError(Exception):
    """Custom exception for invalid product attributes."""
    def __init__(self, message):
        super().__init__(message)