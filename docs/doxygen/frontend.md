# Frontend

O frontend é server-side rendered com templates Jinja2 em
`app/web/templates`.

## Estrutura

- `base.html`: layout global, navegação, CSS base e blocos Jinja.
- `home.html`, `login.html`, `register.html`: entrada e autenticação.
- `products.html`, `product_detail.html`: catálogo e preços observados.
- `shopping_lists.html`, `shopping_list_detail.html`: listas e itens.
- `cart.html`: carrinho e total estimado.
- `stores.html`: locais de compra e mapa Leaflet/OpenStreetMap.
- `pending_items.html`: itens não comprados/pendentes (`US07`).
- `new_product_suggestion.html`, `product_suggestions_admin.html`: sugestão e
  aprovação administrativa de produtos (`AD05`).

## Integração com backend

As rotas HTML ficam em `app/web/html_routes.py`. Elas reutilizam os mesmos
serviços da API JSON, mantendo as regras de negócio fora dos templates.

## Observação

O Doxygen não interpreta Jinja2 como framework frontend específico. Por isso,
esta página documenta a organização e a finalidade dos templates enquanto a
documentação de código cobre as rotas Python que renderizam cada tela.
