from app.domain.exceptions import DuplicateBarcodeError
from app.domain.product import Product

class SQLiteProductRepository:
    def __init__(self, connection):
        self.connection = connection

    def create_table(self):
        cursor = self.connection.cursor()

        cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
        bar_code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL);
        """)
        self.connection.commit()

    def add_product(self, product, quantity):
        cursor = self.connection.cursor()
        if self.get_product_by_bar_code(product.bar_code) is not None:
            raise DuplicateBarcodeError(f"Product with bar code {product.bar_code} already exists.")
        cursor.execute(
        """
        INSERT INTO products (bar_code, name, brand, price, quantity)
        VALUES (?, ?, ?, ?, ?);
        """, (product.bar_code, product.name, product.brand, product.price, quantity))

        self.connection.commit()

    def get_product_by_bar_code(self, bar_code):
        cursor = self.connection.cursor()

        cursor.execute(
        """
        SELECT bar_code, name, brand, price, quantity
        FROM products
        WHERE bar_code = ?;
        """, (bar_code,))

        row = cursor.fetchone()
        if row:
            product = Product(name=row[1], brand=row[2], price=row[3], bar_code=row[0])
            quantity = row[4]
            return product, quantity
        else:
            return None