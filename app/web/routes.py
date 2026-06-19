"""Rotas HTTP da aplicação."""

from flask import Blueprint, jsonify, request

from app.application.product_service import ProductService
from app.web.authorization import admin_required
from app.web.serializers import serialize_product


def create_product_blueprint(
    product_service: ProductService,
) -> Blueprint:
    """AD01/US02/AD02/AD03/RNF02: cria rotas com serviço injetado.

    Pré-condição: product_service deve permitir a criação de produtos.
    Pós-condição: retorna rotas públicas e administrativas configuradas.
    """
    blueprint = Blueprint("products", __name__)

    @blueprint.post("/products")
    @admin_required
    def create_product():
        """AD01/RNF02: permite ao admin criar um produto.

        Pré-condição: sessão admin e JSON com campos obrigatórios.
        Pós-condição: retorna o produto criado em JSON com HTTP 201.
        """
        data = request.get_json()
        product = product_service.create_product(
            name=data["name"],
            brand=data["brand"],
            price=data["price"],
            bar_code=data["bar_code"],
            quantity=data["quantity"],
        )

        return jsonify(serialize_product(product, data["quantity"])), 201

    @blueprint.get("/products")
    def search_products():
        """US02/RNF02: busca pública de produtos por nome ou marca.

        Pré-condição: o parâmetro opcional q contém o texto da busca.
        Pós-condição: retorna uma lista JSON e HTTP 200.
        """
        query = request.args.get("q", "")
        results = product_service.search_products(query)

        return jsonify(
            [serialize_product(product, quantity) for product, quantity in results]
        ), 200

    @blueprint.put("/products/<bar_code>")
    @admin_required
    def update_product(bar_code):
        """AD02/RNF02: permite ao admin editar um produto.

        Pré-condição: sessão admin, produto existente e JSON válido.
        Pós-condição: retorna o produto atualizado em JSON com HTTP 200.
        """
        data = request.get_json()
        product, quantity = product_service.update_product(
            bar_code=bar_code,
            name=data["name"],
            brand=data["brand"],
            price=data["price"],
        )

        return jsonify(serialize_product(product, quantity)), 200

    @blueprint.delete("/products/<bar_code>")
    @admin_required
    def deactivate_product(bar_code):
        """AD02/RNF02: permite ao admin remover logicamente um produto.

        Pré-condição: sessão admin e código de produto cadastrado.
        Pós-condição: desativa o produto e retorna HTTP 204 sem conteúdo.
        """
        product_service.deactivate_product(bar_code)
        return "", 204

    @blueprint.patch("/products/<bar_code>/stock")
    @admin_required
    def update_stock(bar_code):
        """AD03/RNF02: permite ao admin atualizar o estoque.

        Pré-condição: sessão admin, produto existente e quantity válida.
        Pós-condição: retorna produto e estoque atualizado com HTTP 200.
        """
        data = request.get_json()
        product, quantity = product_service.update_stock(
            bar_code=bar_code,
            quantity=data["quantity"],
        )

        return jsonify(serialize_product(product, quantity)), 200

    return blueprint
