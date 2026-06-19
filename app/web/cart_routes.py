"""Rotas HTTP do carrinho em sessão."""

from flask import Blueprint, jsonify, request, session

from app.application.cart_service import CartService
from app.web.serializers import serialize_product


def create_cart_blueprint(cart_service: CartService) -> Blueprint:
    """US04/US05: cria as rotas de carrinho com o serviço injetado.

    Pré-condição: cart_service deve implementar as operações do carrinho.
    Pós-condição: retorna uma blueprint com as rotas /cart.
    """
    blueprint = Blueprint("cart", __name__)

    @blueprint.get("/cart")
    def get_cart():
        """US04: retorna todos os itens do carrinho atual.

        Pré-condição: nenhuma.
        Pós-condição: retorna os itens da sessão com HTTP 200.
        """
        cart = session.get("cart", {})
        return jsonify(
            [
                serialize_product(product, quantity)
                for product, quantity in cart_service.get_items(cart)
            ]
        ), 200

    @blueprint.get("/cart/total")
    def get_cart_total():
        """US05: retorna o total estimado do carrinho atual.

        Pré-condição: os itens da sessão devem referenciar produtos válidos.
        Pós-condição: retorna a soma estimada em JSON com HTTP 200.
        """
        cart = session.get("cart", {})
        items = cart_service.get_items(cart)
        total = cart_service.calculate_total(items)
        return jsonify({"total": total}), 200

    @blueprint.post("/cart/items")
    def add_cart_item():
        """US04: adiciona ou substitui um produto no carrinho.

        Pré-condição: JSON com bar_code e quantity válidos.
        Pós-condição: salva o carrinho na sessão e retorna HTTP 201.
        """
        data = request.get_json()
        cart = dict(session.get("cart", {}))
        product = cart_service.add_item(
            cart=cart,
            bar_code=data["bar_code"],
            quantity=data["quantity"],
        )
        session["cart"] = cart
        return jsonify(
            serialize_product(product, data["quantity"])
        ), 201

    @blueprint.patch("/cart/items/<bar_code>")
    def update_cart_item(bar_code):
        """US04: altera a quantidade de um item do carrinho.

        Pré-condição: item existente e JSON com quantity válida.
        Pós-condição: salva a alteração na sessão e retorna HTTP 200.
        """
        data = request.get_json()
        cart = dict(session.get("cart", {}))
        product = cart_service.update_item(
            cart=cart,
            bar_code=bar_code,
            quantity=data["quantity"],
        )
        session["cart"] = cart
        return jsonify(
            serialize_product(product, data["quantity"])
        ), 200

    @blueprint.delete("/cart/items/<bar_code>")
    def remove_cart_item(bar_code):
        """US04: remove um item do carrinho atual.

        Pré-condição: bar_code deve existir no carrinho.
        Pós-condição: salva a remoção na sessão e retorna HTTP 204.
        """
        cart = dict(session.get("cart", {}))
        cart_service.remove_item(cart, bar_code)
        session["cart"] = cart
        return "", 204

    return blueprint
