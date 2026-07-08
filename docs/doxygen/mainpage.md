# Documentação Doxygen do ProjetoFinalTP2

Esta documentação descreve o backend Flask, a estrutura de templates HTML e os
artefatos de rastreabilidade do Sistema de Gerência de Compras e
Compartilhamento de Preços.

## Como gerar

Na raiz do projeto, instale o Doxygen pelo gerenciador de pacotes do sistema e
execute:

```bash
make doxygen
```

A saída HTML será criada em:

```text
docs_doxygen/html/index.html
```

## Escopo documentado

- Código Python em `app/`.
- Visão de backend em `docs/doxygen/backend.md`.
- Visão de frontend em `docs/doxygen/frontend.md`.
- README do projeto.

## Relação com a entrega da disciplina

A documentação Doxygen complementa os documentos em `docs_entrega_tp2/`, que
contêm rastreabilidade, assertivas, diagramas textuais e relatório final.
