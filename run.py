"""Inicialização local da aplicação com dados de demonstração."""

import os
import sqlite3

from app.infrastructure.demo_seed import seed_demo_data
from app.web.app import create_app


def main() -> None:
    """WEB/DEMO: popula o banco e inicia o servidor Flask.

    Pré-condição: o diretório deve permitir criar o arquivo SQLite.
    Pós-condição: inicia a aplicação local com dados de demonstração.
    """
    database_path = os.environ.get("DATABASE_PATH", "shopping.db")
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    connection = sqlite3.connect(database_path, check_same_thread=False)
    seed_demo_data(connection)
    application = create_app(connection)
    application.run(
        host=host,
        port=port,
        debug=os.environ.get("FLASK_DEBUG") == "1",
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
