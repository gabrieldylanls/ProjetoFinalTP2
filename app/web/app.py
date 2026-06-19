"""Fábrica da aplicação Flask."""

import sqlite3

from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest

from app.domain.exceptions import (
    DuplicateBarcodeError,
    InvalidProductError,
    InvalidQuantityError,
)
from app.web.dependencies import initialize_product_service
from app.web.routes import create_product_blueprint


def create_app(connection: sqlite3.Connection) -> Flask:
    """AD01: cria e configura a aplicação Flask para cadastro de produtos.

    Pré-condição: connection deve ser uma conexão SQLite aberta.
    Pós-condição: retorna a aplicação com a rota POST /products configurada.
    """
    flask_app = Flask(__name__)
    product_service = initialize_product_service(connection)

    flask_app.register_blueprint(
        create_product_blueprint(product_service)
    )
    _register_error_handlers(flask_app)

    return flask_app


def _register_error_handlers(flask_app: Flask) -> None:
    """AD01: registra respostas HTTP para erros do cadastro de produtos."""

    @flask_app.errorhandler(InvalidProductError)
    @flask_app.errorhandler(InvalidQuantityError)
    def handle_validation_error(error):
        return jsonify({"erro": str(error)}), 400

    @flask_app.errorhandler(DuplicateBarcodeError)
    def handle_duplicate_bar_code(error):
        return jsonify({"erro": str(error)}), 409

    @flask_app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify(
            {"erro": "O corpo da requisição deve conter JSON válido."}
        ), 400

    @flask_app.errorhandler(KeyError)
    def handle_missing_field(error):
        field_name = error.args[0]
        return jsonify({"erro": f"O campo '{field_name}' é obrigatório."}), 400
