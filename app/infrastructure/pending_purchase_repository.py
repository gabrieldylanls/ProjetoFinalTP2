"""Persistência SQLite de itens pendentes de compra."""

import sqlite3
from datetime import datetime

from app.domain.pending_purchase_item import PendingPurchaseItem


class SQLitePendingPurchaseRepository:
    """US07: armazena produtos não comprados por usuário."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """US07: inicializa o repositório.

        Pré-condição: connection deve estar aberta.
        Pós-condição: o repositório passa a usar a conexão recebida.
        """
        self.connection = connection

    def create_table(self) -> None:
        """US07: cria a tabela de itens pendentes quando necessário."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_purchase_items (
                user_id INTEGER NOT NULL,
                bar_code TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                source_list_id INTEGER,
                created_at TEXT NOT NULL,
                PRIMARY KEY (user_id, bar_code)
            );
            """
        )
        self.connection.commit()

    def upsert_item(self, item: PendingPurchaseItem) -> PendingPurchaseItem:
        """US07: insere ou soma a quantidade pendente de um produto."""
        self.connection.execute(
            """
            INSERT INTO pending_purchase_items (
                user_id, bar_code, quantity, source_list_id, created_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, bar_code) DO UPDATE SET
                quantity = quantity + excluded.quantity,
                source_list_id = excluded.source_list_id,
                created_at = excluded.created_at;
            """,
            (
                item.user_id,
                item.bar_code,
                item.quantity,
                item.source_list_id,
                item.created_at.isoformat(),
            ),
        )
        self.connection.commit()
        return self.get_item(item.user_id, item.bar_code)

    def get_item(self, user_id: int, bar_code: str) -> PendingPurchaseItem | None:
        """US07: busca um item pendente do usuário."""
        row = self.connection.execute(
            """
            SELECT user_id, bar_code, quantity, source_list_id, created_at
            FROM pending_purchase_items
            WHERE user_id = ? AND bar_code = ?;
            """,
            (user_id, bar_code),
        ).fetchone()
        if row is None:
            return None
        return self._to_item(row)

    def list_items(self, user_id: int) -> list[PendingPurchaseItem]:
        """US07: lista pendências de um usuário."""
        rows = self.connection.execute(
            """
            SELECT user_id, bar_code, quantity, source_list_id, created_at
            FROM pending_purchase_items
            WHERE user_id = ?
            ORDER BY created_at DESC, bar_code;
            """,
            (user_id,),
        ).fetchall()
        return [self._to_item(row) for row in rows]

    def update_quantity(self, user_id: int, bar_code: str, quantity: int) -> None:
        """US07: atualiza a quantidade de um item pendente."""
        self.connection.execute(
            """
            UPDATE pending_purchase_items
            SET quantity = ?
            WHERE user_id = ? AND bar_code = ?;
            """,
            (quantity, user_id, bar_code),
        )
        self.connection.commit()

    def remove_item(self, user_id: int, bar_code: str) -> None:
        """US07: remove um item pendente do usuário."""
        self.connection.execute(
            """
            DELETE FROM pending_purchase_items
            WHERE user_id = ? AND bar_code = ?;
            """,
            (user_id, bar_code),
        )
        self.connection.commit()

    @staticmethod
    def _to_item(row) -> PendingPurchaseItem:
        """US07: converte uma linha SQLite em entidade."""
        return PendingPurchaseItem(
            user_id=row[0],
            bar_code=row[1],
            quantity=row[2],
            source_list_id=row[3],
            created_at=datetime.fromisoformat(row[4]),
        )
