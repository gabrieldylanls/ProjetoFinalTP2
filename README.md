# Sistema de Gerência de Compras e Compartilhamento de Preços

Projeto acadêmico em Python para cadastro de produtos, listas de compras,
carrinho, locais de compra e histórico de preços. A aplicação utiliza Flask,
SQLite por meio do módulo `sqlite3`, templates Jinja2 e testes com `unittest`.

## Requisitos

- Python 3.12 ou superior.
- `venv` e `pip`.

## Instalação

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale a aplicação e as ferramentas de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
```

As dependências de desenvolvimento incluem `coverage` e `ruff`.

## Execução

A aplicação expõe uma factory Flask chamada `create_app(connection)` em
`app/web/app.py`. Ela recebe uma conexão SQLite aberta, permitindo usar banco
em memória nos testes ou um arquivo SQLite na execução local.

Exemplo de inicialização em um shell Python:

```python
import sqlite3

from app.web.app import create_app

connection = sqlite3.connect("shopping.db", check_same_thread=False)
app = create_app(connection)
app.run(debug=True)
```

Para iniciar diretamente com o banco `shopping.db` populado:

```bash
make seed
make run
```

Também é possível executar:

```bash
python -m app.infrastructure.demo_seed
python run.py
```

Abra `http://127.0.0.1:5000/` no navegador. A tela de login fica em
`http://127.0.0.1:5000/login`.

Credenciais de demonstração:

- Administrador: `admin@example.com` / `admin123`
- Usuário comum: `usuario@example.com` / `usuario123`

A população é idempotente: executá-la novamente não duplica usuários ou
produtos fictícios.

## Testes

A suíte permanece baseada exclusivamente em `unittest`:

```bash
python -m unittest discover -s tests
```

O mesmo comando pode ser executado por:

```bash
make test
```

Também existem os alvos `make test-unit` e `make test-integration`.

## Cobertura

Execute os testes coletando cobertura:

```bash
coverage run -m unittest discover -s tests
coverage report --fail-under=80
```

O limite também está definido em `pyproject.toml`. O comando falha quando a
cobertura total fica abaixo de 80%.

Alternativamente:

```bash
make coverage
```

## Análise estática e formatação

Verifique problemas de qualidade e imports:

```bash
ruff check .
```

Formate o código:

```bash
ruff format .
```

Atalhos equivalentes:

```bash
make lint
make format
make quality
```

O alvo `quality` executa testes, cobertura e análise estática.

## Rastreabilidade

Todo teste deve mencionar o ID da estória ou requisito no nome ou na docstring.
Exemplos: `US03`, `AD04`, `RNF02`, `WEB` e `QA`. A mesma identificação deve ser
usada nas docstrings do código relacionado para manter a rastreabilidade entre
requisito, implementação e teste.

## Estrutura

```text
app/
├── domain/          Entidades e regras de negócio puras
├── application/     Serviços e casos de uso
├── infrastructure/  Repositórios SQLite e detalhes técnicos
└── web/             Aplicação Flask, rotas e templates
tests/
├── unit/            Testes de domínio e aplicação
└── integration/     Testes de SQLite e Flask test client
```

Principais arquivos de qualidade:

- `pyproject.toml`: dependências e configuração de coverage e Ruff.
- `Makefile`: atalhos para testes, cobertura, lint e formatação.
- `README.md`: instalação, execução e convenções do projeto.
