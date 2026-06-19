from app.domain.exceptions import InvalidProductError

class Product:
    def __init__(self, name, brand, price, bar_code):
        self.name = name
        self.brand = brand
        self.price = price
        self.bar_code = bar_code

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        # Validate that the name is not empty
        if not value:
            raise InvalidProductError("Product name cannot be empty.")
        # Validate that the name is a string
        if not isinstance(value, str):
            raise InvalidProductError("Product name must be a string.")
        self._name = value
    
    @property
    def brand(self):
        return self._brand
    
    @brand.setter
    def brand(self, value):
        # Validate that the brand is not empty
        if not value:
            raise InvalidProductError("Product brand cannot be empty.")
        # Validate that the brand is a string
        if not isinstance(value, str):
            raise InvalidProductError("Product brand must be a string.")
        self._brand = value

    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        # Validate that the price is a non-negative number
        if not isinstance(value, (int, float)):
            raise InvalidProductError("Product price must be a number.")
        if value < 0:
            raise InvalidProductError("Product price cannot be negative.")
        self._price = value
    
    @property
    def bar_code(self):
        return self._bar_code
    
    @bar_code.setter
    def bar_code(self, value):
        # Validate that the bar code is a string of 13 digits
        if not isinstance(value, str):
            raise InvalidProductError("Product bar code must be a string.")
        if not value.isdigit() or len(value) != 13:
            raise InvalidProductError("Product bar code must be a string of 13 digits.")
        self._bar_code = value

        