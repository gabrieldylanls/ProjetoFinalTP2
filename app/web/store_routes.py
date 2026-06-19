"""Rotas HTTP de locais de compra."""

from flask import Blueprint, jsonify, request

from app.application.store_service import StoreService
from app.web.authorization import admin_required, authenticated_required


def create_store_blueprint(store_service: StoreService) -> Blueprint:
    """US06: cria as rotas de locais com o serviço injetado.

    Pré-condição: store_service deve permitir cadastro e consulta.
    Pós-condição: retorna uma blueprint com as rotas /stores.
    """
    blueprint = Blueprint("stores", __name__)

    @blueprint.post("/stores")
    @admin_required
    def create_store():
        """US06: permite ao admin cadastrar um local.

        Pré-condição: sessão admin e JSON com nome e endereço.
        Pós-condição: retorna o local criado com HTTP 201.
        """
        data = request.get_json()
        store = store_service.create_store(
            name=data["name"],
            address=data["address"],
            observation=data.get("observation"),
        )
        return jsonify(_serialize_store(store)), 201

    @blueprint.get("/stores")
    @authenticated_required
    def list_stores():
        """US06: lista locais para um usuário autenticado.

        Pré-condição: a sessão deve conter usuário autenticado.
        Pós-condição: retorna os locais cadastrados com HTTP 200.
        """
        return jsonify(
            [_serialize_store(store) for store in store_service.list_stores()]
        ), 200

    return blueprint


def _serialize_store(store) -> dict:
    """US06: converte um local de compra para resposta JSON."""
    return {
        "id": store.store_id,
        "name": store.name,
        "address": store.address,
        "observation": store.observation,
    }
