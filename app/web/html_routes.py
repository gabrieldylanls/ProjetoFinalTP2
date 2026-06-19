"""Rotas das páginas HTML mínimas do protótipo."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.application.cart_service import CartService
from app.application.product_service import ProductService
from app.application.user_service import UserService
from app.domain.exceptions import InvalidCredentialsError
from app.web.authorization import admin_required


def create_html_blueprint(
    product_service: ProductService,
    cart_service: CartService,
    user_service: UserService,
) -> Blueprint:
    """US01/WEB: cria páginas HTML reutilizando os serviços existentes.

    Pré-condição: os serviços devem permitir autenticação, catálogo e carrinho.
    Pós-condição: retorna uma blueprint com as páginas do protótipo.
    """
    blueprint = Blueprint("html", __name__)

    @blueprint.get("/")
    def home_page():
        """WEB: exibe a página inicial.

        Pré-condição: nenhuma.
        Pós-condição: retorna a página inicial com HTTP 200.
        """
        return render_template("home.html")

    @blueprint.route("/login", methods=["GET", "POST"])
    def login_page():
        """US01/WEB: exibe e processa o formulário de login.

        Pré-condição: no POST, e-mail e senha devem ser informados.
        Pós-condição: cria a sessão e redireciona ou exibe erro com HTTP 401.
        """
        if request.method == "POST":
            try:
                user = user_service.authenticate_user(
                    email=request.form["email"],
                    password=request.form["password"],
                )
            except InvalidCredentialsError as error:
                return render_template("login.html", error=str(error)), 401

            session.clear()
            session["user_id"] = user.user_id
            session["role"] = user.role
            return redirect(url_for("html.products_page"))

        return render_template("login.html", error=None)

    @blueprint.get("/catalog")
    def products_page():
        """WEB: lista ou busca produtos ativos.

        Pré-condição: o parâmetro opcional q deve ser textual.
        Pós-condição: retorna o catálogo renderizado com HTTP 200.
        """
        query = request.args.get("q", "").strip()
        products = (
            product_service.search_products(query)
            if query
            else product_service.list_products()
        )
        return render_template(
            "products.html",
            products=products,
            query=query,
        )

    @blueprint.route("/admin/products/new", methods=["GET", "POST"])
    @admin_required
    def new_product_page():
        """WEB: exibe e processa o formulário administrativo.

        Pré-condição: sessão admin e campos válidos no envio do formulário.
        Pós-condição: exibe o formulário ou cadastra e redireciona ao catálogo.
        """
        if request.method == "POST":
            product_service.create_product(
                name=request.form["name"],
                brand=request.form["brand"],
                price=float(request.form["price"]),
                bar_code=request.form["bar_code"],
                quantity=int(request.form["quantity"]),
            )
            return redirect(url_for("html.products_page"))

        return render_template("new_product.html")

    @blueprint.get("/cart/view")
    def cart_page():
        """WEB: exibe os itens e o total estimado do carrinho.

        Pré-condição: a sessão pode conter um carrinho válido.
        Pós-condição: retorna o carrinho renderizado com HTTP 200.
        """
        cart = session.get("cart", {})
        items = cart_service.get_items(cart)
        total = cart_service.calculate_total(items)
        return render_template("cart.html", items=items, total=total)

    return blueprint
