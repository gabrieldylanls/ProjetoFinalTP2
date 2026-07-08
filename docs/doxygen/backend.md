# Backend

O backend é uma aplicação Flask organizada em camadas:

- `app/domain`: entidades, validações e exceções de domínio.
- `app/application`: serviços e casos de uso.
- `app/infrastructure`: repositórios SQLite, criação de tabelas e seed.
- `app/web`: factory Flask, rotas JSON, rotas HTML, autorização e serialização.

## Fluxo principal

1. `app/web/app.py` cria a aplicação Flask.
2. `app/web/dependencies.py` inicializa repositórios e serviços.
3. Blueprints em `app/web/*_routes.py` recebem requisições HTTP.
4. Serviços em `app/application` executam regras de aplicação.
5. Repositórios em `app/infrastructure` persistem dados em SQLite.
6. Entidades em `app/domain` garantem pré-condições e invariantes.

## Qualidade e testes

- Testes com `unittest`.
- Cobertura com `coverage`.
- Lint e formatação com `ruff`.
- Rastreabilidade por marcadores como `US03`, `AD05` e `RNF02` em docstrings,
  nomes de testes e documentação.
