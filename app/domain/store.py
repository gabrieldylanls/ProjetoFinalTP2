"""Entidade e regras de validação de locais de compra."""

from app.domain.exceptions import InvalidStoreError


class Store:
    """US06: representa um local de compra disponível."""

    def __init__(
        self,
        store_id: int | None,
        name: str,
        address: str,
        observation: str | None = None,
    ) -> None:
        """US06: cria um local de compra validado.

        Pré-condição: nome e endereço devem ser válidos.
        Pós-condição: cria o local ou lança InvalidStoreError.
        """
        self.store_id = self._validate_store_id(store_id)
        self.name = self._validate_required_text(name, "nome")
        self.address = self._validate_required_text(address, "endereço")
        self.observation = self._validate_observation(observation)

    @staticmethod
    def _validate_store_id(store_id: int | None) -> int | None:
        """US06: valida o identificador opcional do local."""
        if store_id is None:
            return None
        if isinstance(store_id, bool) or not isinstance(store_id, int):
            raise InvalidStoreError(
                "O identificador do local deve ser um número inteiro."
            )
        return store_id

    @staticmethod
    def _validate_required_text(value: str, field_name: str) -> str:
        """US06: valida um campo textual obrigatório."""
        if not isinstance(value, str) or not value.strip():
            raise InvalidStoreError(
                f"O {field_name} do local não pode estar vazio."
            )
        return value.strip()

    @staticmethod
    def _validate_observation(observation: str | None) -> str | None:
        """US06: valida a observação opcional do local."""
        if observation is None:
            return None
        if not isinstance(observation, str):
            raise InvalidStoreError(
                "A observação do local deve ser uma string."
            )
        normalized = observation.strip()
        return normalized or None
