"""Rotas HTTP de itens pendentes de compra."""

from flask import Blueprint, jsonify, request, session

from app.application.pending_purchase_service import PendingPurchaseService
from app.web.authorization import authenticated_required
from app.web.serializers import serialize_pending_item


def create_pending_purchase_blueprint(
    pending_service: PendingPurchaseService,
) -> Blueprint:
    """US07: cria rotas de itens não comprados com serviço injetado."""
    blueprint = Blueprint("pending_purchase", __name__)

    @blueprint.get("/pending-items")
    @authenticated_required
    def list_pending_items():
        """US07: lista itens pendentes do usuário autenticado."""
        details = pending_service.list_pending_items(session["user_id"])
        return jsonify(
            [
                serialize_pending_item(item, product, best_price)
                for item, product, best_price in details
            ]
        ), 200

    @blueprint.post("/shopping-lists/<int:list_id>/items/<bar_code>/pending")
    @authenticated_required
    def mark_pending(list_id, bar_code):
        """US07: marca um item de lista como não comprado."""
        data = request.get_json()
        item = pending_service.mark_item_as_pending(
            user_id=session["user_id"],
            list_id=list_id,
            bar_code=bar_code,
            quantity=data["quantity"],
        )
        return jsonify(serialize_pending_item(item)), 201

    @blueprint.patch("/pending-items/<bar_code>")
    @authenticated_required
    def update_pending_item(bar_code):
        """US07: atualiza a quantidade de um item pendente."""
        data = request.get_json()
        item = pending_service.update_pending_quantity(
            user_id=session["user_id"],
            bar_code=bar_code,
            quantity=data["quantity"],
        )
        return jsonify(serialize_pending_item(item)), 200

    @blueprint.delete("/pending-items/<bar_code>")
    @authenticated_required
    def resolve_pending_item(bar_code):
        """US07: resolve/remover um item pendente."""
        pending_service.resolve_pending_item(session["user_id"], bar_code)
        return "", 204

    return blueprint
