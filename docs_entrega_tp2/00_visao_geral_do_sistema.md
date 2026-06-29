# 00 — Visão geral do sistema

## Nome do sistema

Sistema de Gerência de Compras e Compartilhamento de Preços.

## Objetivo

O sistema tem como objetivo apoiar usuários no planejamento de compras, consulta de produtos, manutenção de listas, uso de carrinho em sessão, visualização de total estimado, consulta de locais de compra e compartilhamento de preços observados por produto e local. Também oferece funcionalidades administrativas para manutenção de catálogo, estoque, locais e métricas simples.

## Escopo implementado

Foram localizados no código os seguintes escopos:

- cadastro, login, logout, sessão Flask e papéis `user` e `admin`;
- cadastro, busca, edição, remoção lógica e estoque de produtos;
- busca pública de produtos por nome ou marca;
- proteção de rotas administrativas por sessão e papel;
- criação de listas de compras, marcação de lista favorita e manutenção de itens;
- carrinho em sessão, alteração de quantidade, remoção e cálculo de total;
- cadastro e listagem de locais de compra;
- busca de loja mais próxima por coordenadas de GPS com `geopy`;
- mapa da loja mais próxima com Leaflet e OpenStreetMap;
- registro e consulta de preços observados por produto e local;
- itens não comprados/pendentes derivados de listas de compras;
- sugestão de produtos por usuários e aprovação/rejeição administrativa;
- painel administrativo com métricas simples;
- templates HTML mínimos para uso do protótipo;
- seed de dados de demonstração.

Foram localizadas implementações para US07 e AD05.

## Tecnologias detectadas no código

- Python 3.12.
- Flask.
- SQLite via módulo padrão `sqlite3`.
- `unittest`.
- `werkzeug.security` para hash e verificação de senha.
- `geopy` para cálculo geodésico da loja mais próxima.
- Leaflet/OpenStreetMap no template HTML de mapa.
- Coverage e Ruff para qualidade.
- Makefile para execução de comandos.

## Estrutura real do projeto

Árvore principal, ignorando `.git`, ambientes virtuais, `__pycache__`, caches e arquivos gerados:

```text
.
├── LEIAME.TXT
├── Makefile
├── README.md
├── app
│   ├── __init__.py
│   ├── application
│   │   ├── admin_metrics_service.py
│   │   ├── cart_service.py
│   │   ├── product_price_service.py
│   │   ├── product_service.py
│   │   ├── shopping_list_service.py
│   │   ├── store_service.py
│   │   └── user_service.py
│   ├── domain
│   │   ├── exceptions.py
│   │   ├── product.py
│   │   ├── product_price.py
│   │   ├── quantity.py
│   │   ├── shopping_list.py
│   │   ├── store.py
│   │   └── user.py
│   ├── infrastructure
│   │   ├── admin_metrics_repository.py
│   │   ├── database.py
│   │   ├── demo_seed.py
│   │   ├── product_price_repository.py
│   │   ├── product_repository.py
│   │   ├── shopping_list_repository.py
│   │   ├── store_repository.py
│   │   └── user_repository.py
│   └── web
│       ├── admin_metrics_routes.py
│       ├── app.py
│       ├── auth_routes.py
│       ├── authorization.py
│       ├── cart_routes.py
│       ├── dependencies.py
│       ├── html_routes.py
│       ├── product_price_routes.py
│       ├── routes.py
│       ├── serializers.py
│       ├── shopping_list_routes.py
│       ├── store_routes.py
│       └── templates
│           ├── admin_dashboard.html
│           ├── base.html
│           ├── cart.html
│           ├── home.html
│           ├── login.html
│           ├── new_product.html
│           ├── new_store.html
│           ├── product_detail.html
│           ├── products.html
│           ├── register.html
│           ├── shopping_list_detail.html
│           ├── shopping_lists.html
│           ├── stores.html
│           └── user_dashboard.html
├── docs_entrega_tp2
├── pyproject.toml
├── run.py
└── tests
    ├── integration
    └── unit
```

## Módulos principais

| Camada | Módulos | Responsabilidade |
|---|---|---|
| Domínio | `product.py`, `user.py`, `shopping_list.py`, `store.py`, `product_price.py`, `quantity.py`, `exceptions.py` | Entidades, validações puras e exceções de regra. |
| Aplicação | `product_service.py`, `user_service.py`, `shopping_list_service.py`, `cart_service.py`, `store_service.py`, `product_price_service.py`, `admin_metrics_service.py` | Casos de uso e coordenação entre domínio e persistência. |
| Infraestrutura | Repositórios SQLite e `demo_seed.py` | Criação de tabelas, consultas SQL, persistência e carga inicial. |
| Web | `app.py`, rotas, autorização, serializadores, templates | Flask, sessão, JSON, HTML e composição de dependências. |
| Testes | `tests/unit`, `tests/integration` | Testes unitários e de integração com SQLite/Flask test client. |

## Rotas principais detectadas

### JSON/API

| Método | Rota | Requisito/uso |
|---|---|---|
| POST | `/auth/register` | US01 cadastro de usuário comum. |
| POST | `/auth/login` | US01 login com sessão. |
| POST | `/auth/logout` | US01 logout. |
| POST | `/products` | AD01 cadastro administrativo de produto. |
| GET | `/products` | US02 busca/listagem de produtos. |
| PUT | `/products/<bar_code>` | AD02 edição de produto. |
| DELETE | `/products/<bar_code>` | AD02 remoção lógica. |
| PATCH | `/products/<bar_code>/stock` | AD03 atualização de estoque. |
| GET | `/admin/metrics` | AD04 métricas administrativas. |
| POST | `/shopping-lists` | US03 criação de lista. |
| POST | `/shopping-lists/<list_id>/items` | US03 adicionar item. |
| PATCH | `/shopping-lists/<list_id>/favorite` | US03 marcar favorita. |
| PATCH | `/shopping-lists/<list_id>/items/<bar_code>` | US03 alterar item. |
| DELETE | `/shopping-lists/<list_id>/items/<bar_code>` | US03 remover item. |
| GET | `/cart` | US04 consultar carrinho. |
| POST | `/cart/items` | US04 adicionar ao carrinho. |
| PATCH | `/cart/items/<bar_code>` | US04 alterar item do carrinho. |
| DELETE | `/cart/items/<bar_code>` | US04 remover item do carrinho. |
| GET | `/cart/total` | US05 total estimado. |
| GET | `/pending-items` | US07 listagem de itens não comprados. |
| POST | `/shopping-lists/<list_id>/items/<bar_code>/pending` | US07 marcar item de lista como pendente. |
| PATCH | `/pending-items/<bar_code>` | US07 alterar quantidade pendente. |
| DELETE | `/pending-items/<bar_code>` | US07 resolver item pendente. |
| POST | `/stores` | US06 cadastro admin de local. |
| GET | `/stores` | US06 listagem autenticada de locais. |
| GET | `/stores/nearest` | US06/GPS loja mais próxima. |
| POST | `/prices` | US06 registro de preço observado. |
| GET | `/products/<bar_code>/prices` | US06 consulta de preços do produto. |
| POST | `/product-suggestions` | AD05 criação de sugestão de produto. |
| GET | `/admin/product-suggestions` | AD05 listagem administrativa de sugestões pendentes. |
| POST | `/admin/product-suggestions/<id>/approve` | AD05 aprovação administrativa de sugestão. |
| POST | `/admin/product-suggestions/<id>/reject` | AD05 rejeição administrativa de sugestão. |

### HTML

| Método | Rota | Template/uso |
|---|---|---|
| GET | `/` | `home.html`. |
| GET/POST | `/login` | `login.html`. |
| GET/POST | `/register` | `register.html`. |
| POST | `/logout` | encerra sessão. |
| GET | `/dashboard` | `user_dashboard.html`. |
| GET | `/admin/dashboard` | `admin_dashboard.html`. |
| GET/POST | `/admin/products/new` | `new_product.html`. |
| GET | `/catalog` | `products.html`. |
| GET | `/products/<bar_code>/view` | `product_detail.html`. |
| GET | `/stores/view` | `stores.html`. |
| GET | `/stores/nearest/view` | `stores.html` com mapa. |
| GET/POST | `/admin/stores/new` | `new_store.html`. |
| GET/POST | `/shopping-lists/view` | `shopping_lists.html`. |
| GET | `/shopping-lists/<list_id>/view` | `shopping_list_detail.html`. |
| POST | `/shopping-lists/<list_id>/items/view` | formulário HTML de item. |
| GET | `/cart/view` | `cart.html`. |
| GET | `/pending-items/view` | `pending_items.html`. |
| POST | `/cart/view/items` | formulário de carrinho. |
| POST | `/cart/view/items/<bar_code>/update` | atualização HTML de carrinho. |
| POST | `/cart/view/items/<bar_code>/remove` | remoção HTML de carrinho. |

## Entidades e tabelas principais

| Entidade/classe | Tabela SQLite | Campos detectados |
|---|---|---|
| `Product` | `products` | `bar_code`, `name`, `brand`, `price`, `quantity`, `active`. |
| `User` | `users` | `id`, `email`, `name`, `password_hash`, `role`. |
| `ShoppingList` | `shopping_lists` | `id`, `user_id`, `name`, `created_at`, `favorite`. |
| `ShoppingListItem` | `shopping_list_items` | `list_id`, `bar_code`, `quantity`. |
| `Store` | `stores` | `id`, `name`, `address`, `observation`, `latitude`, `longitude`. |
| `ProductPrice` | `product_prices` | `id`, `product_bar_code`, `store_id`, `user_id`, `price`, `created_at`. |
| `PendingPurchaseItem` | `pending_purchase_items` | `user_id`, `bar_code`, `quantity`, `source_list_id`, `created_at`. |
| `ProductSuggestion` | `product_suggestions` | `id`, `user_id`, `name`, `brand`, `price`, `bar_code`, `quantity`, `status`, `created_at`, `reviewed_at`, `reviewer_id`, `rejection_reason`. |

## Testes existentes

Foram localizados testes `unittest` em:

- `tests/unit/test_user.py`, `test_user_service.py`;
- `tests/unit/test_product.py`, `test_product_service.py`;
- `tests/unit/test_shopping_list.py`, `test_shopping_list_service.py`;
- `tests/unit/test_cart_service.py`;
- `tests/unit/test_store.py`, `test_store_service.py`;
- `tests/unit/test_product_price_service.py`;
- `tests/unit/test_quality_configuration.py`, `test_web_dependencies.py`;
- `tests/integration/test_auth_routes.py`;
- `tests/integration/test_product_routes.py`, `test_product_repository.py`;
- `tests/integration/test_shopping_list_routes.py`, `test_shopping_list_repository.py`;
- `tests/integration/test_cart_routes.py`;
- `tests/integration/test_store_routes.py`, `test_store_repository.py`;
- `tests/integration/test_product_price_routes.py`, `test_product_price_repository.py`;
- `tests/integration/test_admin_metrics_routes.py`, `test_admin_metrics_repository.py`;
- `tests/integration/test_html_routes.py`, `test_mvp_html_routes.py`;
- `tests/integration/test_demo_seed.py`.

## IDs de estórias e requisitos encontrados

Foram encontrados no código e testes: `US01`, `US02`, `US03`, `US04`, `US05`, `US06`, `US07`, `AD01`, `AD02`, `AD03`, `AD04`, `AD05`, `RNF02`, além de marcadores auxiliares `WEB`, `DEMO` e `QA`.

## Observações sobre aderência ao enunciado

- A aplicação segue arquitetura em camadas simples: domínio, aplicação, infraestrutura e web.
- A persistência usa `sqlite3`, sem SQLAlchemy.
- Os testes usam `unittest`, sem pytest.
- A autorização administrativa é feita na camada web com decorators, preservando serviços sem dependência de sessão.
- O domínio contém validações e exceções específicas.
- O projeto possui rastreabilidade por docstrings e nomes de testes para grande parte das estórias.
- Funcionalidades não localizadas foram documentadas como ausentes, sem inferência de implementação.

## Divisão em grupos funcionais

| Grupo | Tema | Integrantes |
|---|---|---|
| Grupo 1 | Autenticação, usuários, sessão e perfis | Gabriel Balder; Anabel Mendes |
| Grupo 2 | Catálogo, produtos, estoque e painel administrativo | Dionilton Oliveira Silva; Jhonny Rodrigues de Sousa |
| Grupo 3 | Listas de compras, carrinho, preços, locais e total estimado | Gabriel Dylan; Gabriel Campello; Luiz Otávio |
