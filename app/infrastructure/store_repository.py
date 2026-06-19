"""Persistência SQLite de locais de compra."""

import sqlite3

from app.domain.store import Store


class SQLiteStoreRepository:
    """US06: armazena e consulta locais de compra em SQLite."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """Inicializa o repositório de locais.

        Pré-condição: connection deve ser uma conexão SQLite aberta.
        Pós-condição: o repositório utiliza a conexão recebida.
        """
        self.connection = connection

    def create_table(self) -> None:
        """US06: cria a tabela de locais quando necessário.

        Pré-condição: a conexão deve estar aberta.
        Pós-condição: a tabela stores existe.
        """
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                observation TEXT
            );
            """
        )
        self.connection.commit()

    def add_store(self, store: Store) -> None:
        """US06: persiste um local de compra.

        Pré-condição: store deve ser válido e ainda não persistido.
        Pós-condição: o local recebe id e é salvo no banco.
        """
        cursor = self.connection.execute(
            """
            INSERT INTO stores (name, address, observation)
            VALUES (?, ?, ?);
            """,
            (store.name, store.address, store.observation),
        )
        self.connection.commit()
        store.store_id = cursor.lastrowid

    def list_stores(self) -> list[Store]:
        """US06: lista os locais cadastrados.

        Pré-condição: a tabela stores deve existir.
        Pós-condição: retorna os locais ordenados por nome e id.
        """
        rows = self.connection.execute(
            """
            SELECT id, name, address, observation
            FROM stores
            ORDER BY name COLLATE NOCASE, id;
            """
        ).fetchall()
        return [
            Store(
                store_id=row[0],
                name=row[1],
                address=row[2],
                observation=row[3],
            )
            for row in rows
        ]
