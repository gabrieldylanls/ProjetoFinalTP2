"""Serializadores compartilhados da camada web."""


def serialize_product(product, quantity: int) -> dict:
    """AD01/US02/US04: converte produto e quantidade para JSON.

    Pré-condição: product deve expor os atributos públicos do catálogo.
    Pós-condição: retorna um dicionário serializável sem alterar o produto.
    """
    return {
        "name": product.name,
        "brand": product.brand,
        "price": product.price,
        "bar_code": product.bar_code,
        "quantity": quantity,
    }


def serialize_pending_item(item, product=None, best_price=None) -> dict:
    """US07: converte item pendente para JSON."""
    data = {
        "user_id": item.user_id,
        "bar_code": item.bar_code,
        "quantity": item.quantity,
        "source_list_id": item.source_list_id,
        "created_at": item.created_at.isoformat(),
    }
    if product is not None:
        data["product"] = {
            "name": product.name,
            "brand": product.brand,
            "price": product.price,
            "bar_code": product.bar_code,
        }
    if best_price is not None:
        data["best_price"] = {
            "price": best_price[0],
            "created_at": best_price[1],
            "store_id": best_price[2],
            "store_name": best_price[3],
        }
    else:
        data["best_price"] = None
    return data


def serialize_product_suggestion(suggestion) -> dict:
    """AD05: converte sugestão de produto para JSON."""
    return {
        "id": suggestion.suggestion_id,
        "user_id": suggestion.user_id,
        "name": suggestion.name,
        "brand": suggestion.brand,
        "price": suggestion.price,
        "bar_code": suggestion.bar_code,
        "quantity": suggestion.quantity,
        "status": suggestion.status,
        "created_at": suggestion.created_at.isoformat(),
        "reviewed_at": suggestion.reviewed_at.isoformat()
        if suggestion.reviewed_at is not None
        else None,
        "reviewer_id": suggestion.reviewer_id,
        "rejection_reason": suggestion.rejection_reason,
    }
