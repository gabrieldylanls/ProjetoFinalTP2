"""Persistência SQLite de sugestões de produtos."""

import sqlite3
from datetime import datetime

from app.domain.product_suggestion import ProductSuggestion


class SQLiteProductSuggestionRepository:
    """AD05: armazena sugestões de produtos feitas por usuários."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        """AD05: inicializa o repositório."""
        self.connection = connection

    def create_table(self) -> None:
        """AD05: cria a tabela de sugestões quando necessário."""
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS product_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                price REAL NOT NULL,
                bar_code TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                reviewed_at TEXT,
                reviewer_id INTEGER,
                rejection_reason TEXT
            );
            """
        )
        self.connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_product_suggestions_status
            ON product_suggestions (status, created_at);
            """
        )
        self.connection.commit()

    def add_suggestion(self, suggestion: ProductSuggestion) -> None:
        """AD05: persiste uma nova sugestão pendente."""
        cursor = self.connection.execute(
            """
            INSERT INTO product_suggestions (
                user_id, name, brand, price, bar_code, quantity, status,
                created_at, reviewed_at, reviewer_id, rejection_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            self._to_parameters(suggestion),
        )
        self.connection.commit()
        suggestion.suggestion_id = cursor.lastrowid

    def get_suggestion_by_id(
        self,
        suggestion_id: int,
    ) -> ProductSuggestion | None:
        """AD05: busca uma sugestão pelo identificador."""
        row = self.connection.execute(
            """
            SELECT id, user_id, name, brand, price, bar_code, quantity, status,
                   created_at, reviewed_at, reviewer_id, rejection_reason
            FROM product_suggestions
            WHERE id = ?;
            """,
            (suggestion_id,),
        ).fetchone()
        if row is None:
            return None
        return self._to_suggestion(row)

    def list_pending_suggestions(self) -> list[ProductSuggestion]:
        """AD05: lista sugestões pendentes da mais antiga para a mais nova."""
        rows = self.connection.execute(
            """
            SELECT id, user_id, name, brand, price, bar_code, quantity, status,
                   created_at, reviewed_at, reviewer_id, rejection_reason
            FROM product_suggestions
            WHERE status = 'pending'
            ORDER BY created_at, id;
            """
        ).fetchall()
        return [self._to_suggestion(row) for row in rows]

    def update_review(self, suggestion: ProductSuggestion) -> None:
        """AD05: persiste o resultado da revisão administrativa."""
        self.connection.execute(
            """
            UPDATE product_suggestions
            SET status = ?,
                reviewed_at = ?,
                reviewer_id = ?,
                rejection_reason = ?
            WHERE id = ?;
            """,
            (
                suggestion.status,
                suggestion.reviewed_at.isoformat()
                if suggestion.reviewed_at is not None
                else None,
                suggestion.reviewer_id,
                suggestion.rejection_reason,
                suggestion.suggestion_id,
            ),
        )
        self.connection.commit()

    @staticmethod
    def _to_parameters(suggestion: ProductSuggestion) -> tuple:
        """AD05: prepara uma sugestão para INSERT."""
        return (
            suggestion.user_id,
            suggestion.name,
            suggestion.brand,
            suggestion.price,
            suggestion.bar_code,
            suggestion.quantity,
            suggestion.status,
            suggestion.created_at.isoformat(),
            suggestion.reviewed_at.isoformat()
            if suggestion.reviewed_at is not None
            else None,
            suggestion.reviewer_id,
            suggestion.rejection_reason,
        )

    @staticmethod
    def _to_suggestion(row) -> ProductSuggestion:
        """AD05: converte uma linha SQLite em sugestão."""
        return ProductSuggestion(
            suggestion_id=row[0],
            user_id=row[1],
            name=row[2],
            brand=row[3],
            price=row[4],
            bar_code=row[5],
            quantity=row[6],
            status=row[7],
            created_at=datetime.fromisoformat(row[8]),
            reviewed_at=datetime.fromisoformat(row[9]) if row[9] else None,
            reviewer_id=row[10],
            rejection_reason=row[11],
        )
