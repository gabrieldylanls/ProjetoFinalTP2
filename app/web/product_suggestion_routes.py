"""Rotas HTTP de sugestões de produtos."""

from flask import Blueprint, jsonify, request, session

from app.application.product_suggestion_service import ProductSuggestionService
from app.web.authorization import admin_required, authenticated_required
from app.web.serializers import serialize_product_suggestion


def create_product_suggestion_blueprint(
    suggestion_service: ProductSuggestionService,
) -> Blueprint:
    """AD05: cria rotas de sugestão e revisão de produtos."""
    blueprint = Blueprint("product_suggestions", __name__)

    @blueprint.post("/product-suggestions")
    @authenticated_required
    def suggest_product():
        """AD05: registra sugestão de produto de usuário autenticado."""
        data = request.get_json()
        suggestion = suggestion_service.suggest_product(
            user_id=session["user_id"],
            name=data["name"],
            brand=data["brand"],
            price=data["price"],
            bar_code=data["bar_code"],
            quantity=data["quantity"],
        )
        return jsonify(serialize_product_suggestion(suggestion)), 201

    @blueprint.get("/admin/product-suggestions")
    @admin_required
    def list_pending_suggestions():
        """AD05: lista sugestões pendentes para administradores."""
        return jsonify(
            [
                serialize_product_suggestion(suggestion)
                for suggestion in suggestion_service.list_pending_suggestions()
            ]
        ), 200

    @blueprint.post("/admin/product-suggestions/<int:suggestion_id>/approve")
    @admin_required
    def approve_suggestion(suggestion_id):
        """AD05: aprova uma sugestão e cria o produto no catálogo."""
        suggestion = suggestion_service.approve_suggestion(
            suggestion_id=suggestion_id,
            reviewer_id=session["user_id"],
        )
        return jsonify(serialize_product_suggestion(suggestion)), 200

    @blueprint.post("/admin/product-suggestions/<int:suggestion_id>/reject")
    @admin_required
    def reject_suggestion(suggestion_id):
        """AD05: rejeita uma sugestão pendente."""
        data = request.get_json(silent=True) or {}
        suggestion = suggestion_service.reject_suggestion(
            suggestion_id=suggestion_id,
            reviewer_id=session["user_id"],
            rejection_reason=data.get("rejection_reason"),
        )
        return jsonify(serialize_product_suggestion(suggestion)), 200

    return blueprint
