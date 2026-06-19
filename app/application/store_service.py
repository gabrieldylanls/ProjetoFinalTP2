"""Casos de uso relacionados a locais de compra."""

from app.domain.store import Store


class StoreService:
    """US06: coordena cadastro e consulta de locais de compra."""

    def __init__(self, store_repository) -> None:
        """Inicializa o serviço de locais.

        Pré-condição: o repositório deve implementar inclusão e listagem.
        Pós-condição: o serviço fica pronto para gerenciar locais.
        """
        self.store_repository = store_repository

    def create_store(
        self,
        name: str,
        address: str,
        observation: str | None = None,
    ) -> Store:
        """US06: cria e persiste um local de compra.

        Pré-condição: nome, endereço e observação devem ser válidos.
        Pós-condição: retorna o local criado e persistido.
        """
        store = Store(
            store_id=None,
            name=name,
            address=address,
            observation=observation,
        )
        self.store_repository.add_store(store)
        return store

    def list_stores(self) -> list[Store]:
        """US06: lista os locais de compra disponíveis.

        Pré-condição: o repositório deve estar inicializado.
        Pós-condição: retorna todos os locais ordenados pelo repositório.
        """
        return self.store_repository.list_stores()
