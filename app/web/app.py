"""Fábrica da aplicação Flask."""

import os
import sqlite3

from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest

from app.domain.exceptions import (
    CartItemNotFoundError,
    DuplicateBarcodeError,
    DuplicateEmailError,
    InvalidCartError,
    InvalidCredentialsError,
    InvalidPendingPurchaseItemError,
    InvalidProductError,
    InvalidProductPriceError,
    InvalidProductSuggestionError,
    InvalidQuantityError,
    InvalidShoppingListError,
    InvalidStoreError,
    InvalidUserError,
    PendingPurchaseItemNotFoundError,
    ProductNotFoundError,
    ProductSuggestionConflictError,
    ProductSuggestionNotFoundError,
    ShoppingListItemNotFoundError,
    ShoppingListNotFoundError,
    StoreNotFoundError,
)
from app.web.admin_metrics_routes import create_admin_metrics_blueprint
from app.web.auth_routes import create_auth_blueprint
from app.web.cart_routes import create_cart_blueprint
from app.web.dependencies import (
    initialize_admin_metrics_service,
    initialize_cart_service,
    initialize_pending_purchase_service,
    initialize_product_price_service,
    initialize_product_service,
    initialize_product_suggestion_service,
    initialize_shopping_list_service,
    initialize_store_service,
    initialize_user_service,
)
from app.web.html_routes import create_html_blueprint
from app.web.pending_purchase_routes import create_pending_purchase_blueprint
from app.web.product_price_routes import create_product_price_blueprint
from app.web.product_suggestion_routes import create_product_suggestion_blueprint
from app.web.routes import create_product_blueprint
from app.web.shopping_list_routes import create_shopping_list_blueprint
from app.web.store_routes import create_store_blueprint


def create_app(connection: sqlite3.Connection) -> Flask:
    """AD01/AD02/AD03/AD04/US01-US06/RNF02: cria a aplicação Flask.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna a aplicação com autenticação e autorização.
    """
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "development-secret-key",
    )
    product_service = initialize_product_service(connection)
    cart_service = initialize_cart_service(product_service)
    user_service = initialize_user_service(connection)
    shopping_list_service = initialize_shopping_list_service(connection)
    store_service = initialize_store_service(connection)
    product_price_service = initialize_product_price_service(
        connection,
        product_service,
        store_service,
    )
    pending_service = initialize_pending_purchase_service(connection)
    suggestion_service = initialize_product_suggestion_service(
        connection,
        product_service,
    )
    admin_metrics_service = initialize_admin_metrics_service(connection)

    flask_app.register_blueprint(create_product_blueprint(product_service))
    flask_app.register_blueprint(create_cart_blueprint(cart_service))
    flask_app.register_blueprint(create_auth_blueprint(user_service))
    flask_app.register_blueprint(create_shopping_list_blueprint(shopping_list_service))
    flask_app.register_blueprint(create_store_blueprint(store_service))
    flask_app.register_blueprint(create_product_price_blueprint(product_price_service))
    flask_app.register_blueprint(create_pending_purchase_blueprint(pending_service))
    flask_app.register_blueprint(
        create_product_suggestion_blueprint(suggestion_service)
    )
    flask_app.register_blueprint(create_admin_metrics_blueprint(admin_metrics_service))
    flask_app.register_blueprint(
        create_html_blueprint(
            product_service,
            cart_service,
            user_service,
            store_service,
            admin_metrics_service,
            product_price_service,
            shopping_list_service,
            pending_service,
            suggestion_service,
        )
    )
    _register_error_handlers(flask_app)

    return flask_app


def _register_error_handlers(flask_app: Flask) -> None:
    """AD01/US01/AD02: registra respostas HTTP para erros esperados."""

    @flask_app.errorhandler(InvalidProductError)
    @flask_app.errorhandler(InvalidProductPriceError)
    @flask_app.errorhandler(InvalidCartError)
    @flask_app.errorhandler(InvalidQuantityError)
    @flask_app.errorhandler(InvalidShoppingListError)
    @flask_app.errorhandler(InvalidStoreError)
    @flask_app.errorhandler(InvalidUserError)
    @flask_app.errorhandler(InvalidPendingPurchaseItemError)
    @flask_app.errorhandler(InvalidProductSuggestionError)
    def handle_validation_error(error):
        return jsonify({"erro": str(error)}), 400

    @flask_app.errorhandler(DuplicateBarcodeError)
    @flask_app.errorhandler(DuplicateEmailError)
    @flask_app.errorhandler(ProductSuggestionConflictError)
    def handle_duplicate_bar_code(error):
        return jsonify({"erro": str(error)}), 409

    @flask_app.errorhandler(InvalidCredentialsError)
    def handle_invalid_credentials(error):
        return jsonify({"erro": str(error)}), 401

    @flask_app.errorhandler(ProductNotFoundError)
    @flask_app.errorhandler(CartItemNotFoundError)
    @flask_app.errorhandler(ShoppingListItemNotFoundError)
    @flask_app.errorhandler(ShoppingListNotFoundError)
    @flask_app.errorhandler(StoreNotFoundError)
    @flask_app.errorhandler(PendingPurchaseItemNotFoundError)
    @flask_app.errorhandler(ProductSuggestionNotFoundError)
    def handle_product_not_found(error):
        return jsonify({"erro": str(error)}), 404

    @flask_app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({"erro": "O corpo da requisição deve conter JSON válido."}), 400

    @flask_app.errorhandler(KeyError)
    def handle_missing_field(error):
        field_name = error.args[0]
        return jsonify({"erro": f"O campo '{field_name}' é obrigatório."}), 400
