import unittest

from app.domain.exceptions import InvalidProductError
from app.domain.product import Product


class TestProductCreation(unittest.TestCase):
    """Testa a criação e as regras de validação de produtos."""

    def create_product(self, **changes):
        """Cria um produto válido com alterações pontuais."""
        data = {
            "name": "Produto de teste",
            "brand": "Marca de teste",
            "price": 10.0,
            "bar_code": "1234567890123",
        }
        data.update(changes)
        return Product(**data)

    def test_create_product(self):
        """Deve criar um produto com atributos válidos."""
        product = self.create_product()

        self.assertEqual(product.name, "Produto de teste")
        self.assertEqual(product.brand, "Marca de teste")
        self.assertEqual(product.price, 10.0)
        self.assertEqual(product.bar_code, "1234567890123")

    def test_accept_zero_price(self):
        """Deve aceitar preço zero como valor-limite válido."""
        product = self.create_product(price=0)

        self.assertEqual(product.price, 0)

    def test_reject_negative_price(self):
        """Deve rejeitar preço negativo."""
        with self.assertRaisesRegex(
            InvalidProductError,
            "^O preço do produto não pode ser negativo\\.$",
        ):
            self.create_product(price=-0.01)

    def test_reject_invalid_price_types(self):
        """Deve rejeitar tipos não numéricos e booleanos como preço."""
        invalid_prices = (True, "10.00", None, [], object())

        for price in invalid_prices:
            with self.subTest(price=price):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^O preço do produto deve ser um número\\.$",
                ):
                    self.create_product(price=price)

    def test_reject_non_finite_price(self):
        """Deve rejeitar NaN e valores infinitos."""
        for price in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(price=price):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^O preço do produto deve ser finito\\.$",
                ):
                    self.create_product(price=price)

    def test_reject_invalid_name_types(self):
        """Deve rejeitar nome que não seja uma string."""
        for name in (None, 10, True, []):
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^O nome do produto deve ser uma string\\.$",
                ):
                    self.create_product(name=name)

    def test_reject_blank_name(self):
        """Deve rejeitar nome vazio ou composto apenas por espaços."""
        for name in ("", " ", "\t\n"):
            with self.subTest(name=repr(name)):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^O nome do produto não pode estar vazio\\.$",
                ):
                    self.create_product(name=name)

    def test_reject_invalid_brand_types(self):
        """Deve rejeitar marca que não seja uma string."""
        for brand in (None, 10, True, []):
            with self.subTest(brand=brand):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^A marca do produto deve ser uma string\\.$",
                ):
                    self.create_product(brand=brand)

    def test_reject_blank_brand(self):
        """Deve rejeitar marca vazia ou composta apenas por espaços."""
        for brand in ("", " ", "\t\n"):
            with self.subTest(brand=repr(brand)):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^A marca do produto não pode estar vazia\\.$",
                ):
                    self.create_product(brand=brand)

    def test_accept_bar_code_with_exact_length(self):
        """Deve aceitar código de barras com exatamente 13 dígitos ASCII."""
        product = self.create_product(bar_code="0000000000000")

        self.assertEqual(product.bar_code, "0000000000000")

    def test_reject_invalid_bar_code_types(self):
        """Deve rejeitar código de barras que não seja uma string."""
        for bar_code in (None, 1234567890123, True, []):
            with self.subTest(bar_code=bar_code):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^O código de barras deve ser uma string\\.$",
                ):
                    self.create_product(bar_code=bar_code)

    def test_reject_invalid_bar_code_format(self):
        """Deve rejeitar tamanho, caracteres ou dígitos inválidos."""
        invalid_bar_codes = (
            "123456789012",
            "12345678901234",
            "123456789012A",
            "١٢٣٤٥٦٧٨٩٠١٢٣",
        )

        for bar_code in invalid_bar_codes:
            with self.subTest(bar_code=bar_code):
                with self.assertRaisesRegex(
                    InvalidProductError,
                    "^O código de barras deve conter exatamente 13 dígitos ASCII\\.$",
                ):
                    self.create_product(bar_code=bar_code)


class TestProductUpdate(unittest.TestCase):
    """Testa alterações nos atributos de um produto existente."""

    def setUp(self):
        self.product = Product(
            name="Produto de teste",
            brand="Marca de teste",
            price=10.0,
            bar_code="1234567890123",
        )

    def test_update_product_price(self):
        """Deve atualizar o preço para um valor válido."""
        self.product.price = 20.0

        self.assertEqual(self.product.price, 20.0)

    def test_reject_invalid_price_update(self):
        """Deve manter o preço anterior quando o novo valor for inválido."""
        with self.assertRaises(InvalidProductError):
            self.product.price = -5.0

        self.assertEqual(self.product.price, 10.0)

    def test_reject_invalid_bar_code_update(self):
        """Deve manter o código anterior quando o novo valor for inválido."""
        with self.assertRaises(InvalidProductError):
            self.product.bar_code = "123456789012"

        self.assertEqual(self.product.bar_code, "1234567890123")

    def test_reject_invalid_name_update(self):
        """Deve manter o nome anterior quando o novo valor for inválido."""
        with self.assertRaises(InvalidProductError):
            self.product.name = " "

        self.assertEqual(self.product.name, "Produto de teste")

    def test_reject_invalid_brand_update(self):
        """Deve manter a marca anterior quando o novo valor for inválido."""
        with self.assertRaises(InvalidProductError):
            self.product.brand = " "

        self.assertEqual(self.product.brand, "Marca de teste")
