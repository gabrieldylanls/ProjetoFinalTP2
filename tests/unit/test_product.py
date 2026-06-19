import unittest

from app.domain.product import Product
from app.domain.exceptions import InvalidProductError

class TestProduct(unittest.TestCase):
    def test_create_product(self):
        """Product should be created with valid attributes."""
        product = Product(
            name="Test product",
            brand="Test brand",
            price=10.0,
            bar_code="1234567890123"
            )
        self.assertEqual(product.name, "Test product")
        self.assertEqual(product.brand, "Test brand")
        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.bar_code, "1234567890123")

    def test_create_product_invalid_price(self):
        """Creating a product with a negative price 
           should raise an InvalidProductError."""
        with self.assertRaises(InvalidProductError):
            Product(
                name="Test product",
                brand="Test brand",
                price=-10.0,
                bar_code="1234567890123"
            )
            self.assertRaises(InvalidProductError)
    
    def test_create_product_invalid_bar_code(self):
        """Creating a product with an invalid bar code 
           should raise an InvalidProductError."""
        with self.assertRaises(InvalidProductError):
            Product(
                name="Test product",
                brand="Test brand",
                price=10.0,
                bar_code="invalid_bar_code"
            )
            self.assertRaises(InvalidProductError)
    
    def test_create_product_empty_name(self):
        """Creating a product with an empty name 
           should raise an InvalidProductError."""
        with self.assertRaises(InvalidProductError):
            Product(
                name="",
                brand="Test brand",
                price=10.0,
                bar_code="1234567890123"
            )
            self.assertRaises(InvalidProductError)

    def test_create_product_empty_brand(self):
        """Creating a product with an empty brand 
           should raise an InvalidProductError."""
        with self.assertRaises(InvalidProductError):
            Product(
                name="Test product",
                brand="",
                price=10.0,
                bar_code="1234567890123"
            )
            self.assertRaises(InvalidProductError)

