"""Rotas das páginas HTML do site."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from app.application.admin_metrics_service import AdminMetricsService
from app.application.cart_service import CartService
from app.application.pending_purchase_service import PendingPurchaseService
from app.application.product_price_service import ProductPriceService
from app.application.product_service import ProductService
from app.application.product_suggestion_service import ProductSuggestionService
from app.application.shopping_list_service import ShoppingListService
from app.application.store_service import StoreService
from app.application.user_service import UserService
from app.domain.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidUserError,
)
from app.web.authorization import admin_required, authenticated_required


def create_html_blueprint(
    product_service: ProductService,
    cart_service: CartService,
    user_service: UserService,
    store_service: StoreService,
    admin_metrics_service: AdminMetricsService,
    product_price_service: ProductPriceService,
    shopping_list_service: ShoppingListService,
    pending_service: PendingPurchaseService,
    suggestion_service: ProductSuggestionService,
) -> Blueprint:
    """US01-US07/AD04/AD05/WEB: cria páginas usando serviços injetados.

    Pré-condição: os serviços devem estar inicializados.
    Pós-condição: retorna a blueprint com os fluxos HTML do site.
    """
    blueprint = Blueprint("html", __name__)

    @blueprint.get("/")
    def home_page():
        """WEB: exibe a página inicial."""
        return render_template("home.html")

    @blueprint.route("/login", methods=["GET", "POST"])
    def login_page():
        """US01/WEB: autentica usuário ou administrador."""
        if request.method == "POST":
            try:
                user = user_service.authenticate_user(
                    email=request.form["email"],
                    password=request.form["password"],
                )
            except InvalidCredentialsError as error:
                return render_template("login.html", error=str(error)), 401

            _start_session(user)
            destination = (
                "html.admin_dashboard" if user.role == "admin" else "html.products_page"
            )
            return redirect(url_for(destination))
        return render_template("login.html", error=None)

    @blueprint.route("/register", methods=["GET", "POST"])
    def register_page():
        """US01/WEB: cadastra somente usuário comum."""
        if request.method == "POST":
            try:
                user = user_service.create_user(
                    name=request.form["name"],
                    email=request.form["email"],
                    password=request.form["password"],
                    role="user",
                )
            except (DuplicateEmailError, InvalidUserError) as error:
                status = 409 if isinstance(error, DuplicateEmailError) else 400
                return render_template("register.html", error=str(error)), status

            _start_session(user)
            return redirect(url_for("html.user_dashboard"))
        return render_template("register.html", error=None)

    @blueprint.post("/logout")
    def logout_page():
        """US01/WEB: encerra a sessão e volta ao login."""
        session.clear()
        return redirect(url_for("html.login_page"))

    @blueprint.get("/dashboard")
    @authenticated_required
    def user_dashboard():
        """WEB: exibe o painel do usuário autenticado."""
        return render_template(
            "user_dashboard.html",
            cart_count=sum(session.get("cart", {}).values()),
            store_count=len(store_service.list_stores()),
        )

    @blueprint.route("/shopping-lists/view", methods=["GET", "POST"])
    @authenticated_required
    def shopping_lists_page():
        """US03/WEB: cria e lista as listas de compras do usuário.

        Pré-condição: a sessão deve conter usuário autenticado.
        Pós-condição: cria uma lista ou renderiza somente as listas próprias.
        """
        if request.method == "POST":
            shopping_list_service.create_shopping_list(
                user_id=session["user_id"],
                name=request.form["name"],
            )
            return redirect(url_for("html.shopping_lists_page"))

        return render_template(
            "shopping_lists.html",
            shopping_lists=shopping_list_service.list_shopping_lists(
                session["user_id"]
            ),
        )

    @blueprint.post("/shopping-lists/<int:list_id>/favorite/view")
    @authenticated_required
    def favorite_shopping_list_page(list_id):
        """US03/WEB: marca uma lista própria como favorita.

        Pré-condição: a lista deve pertencer ao usuário autenticado.
        Pós-condição: atualiza a favorita e redireciona à listagem.
        """
        shopping_list_service.mark_as_favorite(
            user_id=session["user_id"],
            list_id=list_id,
        )
        return redirect(url_for("html.shopping_lists_page"))

    @blueprint.get("/shopping-lists/<int:list_id>/view")
    @authenticated_required
    def shopping_list_detail_page(list_id):
        """US03/WEB: exibe itens e produtos disponíveis para inclusão.

        Pré-condição: a lista deve pertencer ao usuário autenticado.
        Pós-condição: retorna o detalhe da lista com HTTP 200.
        """
        query = request.args.get("q", "").strip()
        shopping_list, items = shopping_list_service.get_shopping_list_details(
            user_id=session["user_id"],
            list_id=list_id,
        )
        products, _, _, _ = product_service.list_products_page(
            query=query,
            page=1,
            page_size=50,
        )
        return render_template(
            "shopping_list_detail.html",
            shopping_list=shopping_list,
            items=items,
            products=products,
            query=query,
        )

    @blueprint.post("/shopping-lists/<int:list_id>/items/<bar_code>/pending/view")
    @authenticated_required
    def mark_pending_item_page(list_id, bar_code):
        """US07/WEB: marca item de lista como não comprado."""
        pending_service.mark_item_as_pending(
            user_id=session["user_id"],
            list_id=list_id,
            bar_code=bar_code,
            quantity=int(request.form["quantity"]),
        )
        return redirect(url_for("html.shopping_list_detail_page", list_id=list_id))

    @blueprint.post("/shopping-lists/<int:list_id>/items/view")
    @authenticated_required
    def add_shopping_list_item_page(list_id):
        """US03/WEB: adiciona um produto à lista pelo formulário.

        Pré-condição: lista própria, produto existente e quantidade positiva.
        Pós-condição: persiste o item e redireciona ao detalhe.
        """
        shopping_list_service.add_item(
            user_id=session["user_id"],
            list_id=list_id,
            bar_code=request.form["bar_code"],
            quantity=int(request.form["quantity"]),
        )
        return redirect(url_for("html.shopping_list_detail_page", list_id=list_id))

    @blueprint.get("/catalog")
    def products_page():
        """US02/US06/WEB: busca produtos e filtra por loja."""
        query = request.args.get("q", "").strip()
        page = request.args.get("page", default=1, type=int) or 1
        store_id = request.args.get("store_id", type=int)
        selected_store = None
        observed_prices = {}

        if store_id:
            selected_store = store_service.get_store(store_id)
            store_items, current_page, total_pages, total_products = (
                product_price_service.list_store_products_page(
                    store_id=store_id,
                    query=query,
                    page=page,
                )
            )
            products = [(product, quantity) for product, quantity, _ in store_items]
            observed_prices = {
                product.bar_code: price for product, _, price in store_items
            }
        else:
            products, current_page, total_pages, total_products = (
                product_service.list_products_page(query=query, page=page)
            )

        return render_template(
            "products.html",
            products=products,
            query=query,
            stores=store_service.list_stores(),
            store_id=store_id,
            selected_store=selected_store,
            observed_prices=observed_prices,
            page=current_page,
            total_pages=total_pages,
            total_products=total_products,
        )

    @blueprint.get("/stores/view")
    @authenticated_required
    def stores_page():
        """US06/WEB: exibe os locais de compra."""
        return render_template(
            "stores.html",
            stores=store_service.list_stores(),
            nearest_store=None,
            distance_km=None,
            user_latitude=None,
            user_longitude=None,
        )

    @blueprint.get("/stores/nearest/view")
    @authenticated_required
    def nearest_store_page():
        """US06/GPS/WEB: exibe a loja mais próxima usando posição do usuário.

        Pré-condição: sessão autenticada e query com latitude e longitude.
        Pós-condição: renderiza a loja mais próxima calculada pelo serviço.
        """
        nearest_store, distance_km = store_service.find_nearest_store(
            latitude=request.args["latitude"],
            longitude=request.args["longitude"],
        )
        return render_template(
            "stores.html",
            stores=store_service.list_stores(),
            nearest_store=nearest_store,
            distance_km=distance_km,
            user_latitude=float(request.args["latitude"]),
            user_longitude=float(request.args["longitude"]),
        )

    @blueprint.route("/admin/stores/new", methods=["GET", "POST"])
    @admin_required
    def new_store_page():
        """US06/WEB: cadastra um local pela interface administrativa."""
        if request.method == "POST":
            store_service.create_store(
                name=request.form["name"],
                address=request.form["address"],
                observation=request.form.get("observation"),
                latitude=_optional_float(request.form.get("latitude")),
                longitude=_optional_float(request.form.get("longitude")),
            )
            return redirect(url_for("html.stores_page"))
        return render_template("new_store.html")

    @blueprint.get("/admin/product-suggestions/view")
    @admin_required
    def product_suggestions_admin_page():
        """AD05/WEB: exibe sugestões pendentes para revisão."""
        return render_template(
            "product_suggestions_admin.html",
            suggestions=suggestion_service.list_pending_suggestions(),
        )

    @blueprint.post("/admin/product-suggestions/<int:suggestion_id>/approve/view")
    @admin_required
    def approve_product_suggestion_page(suggestion_id):
        """AD05/WEB: aprova uma sugestão de produto."""
        suggestion_service.approve_suggestion(
            suggestion_id=suggestion_id,
            reviewer_id=session["user_id"],
        )
        return redirect(url_for("html.product_suggestions_admin_page"))

    @blueprint.post("/admin/product-suggestions/<int:suggestion_id>/reject/view")
    @admin_required
    def reject_product_suggestion_page(suggestion_id):
        """AD05/WEB: rejeita uma sugestão de produto."""
        suggestion_service.reject_suggestion(
            suggestion_id=suggestion_id,
            reviewer_id=session["user_id"],
            rejection_reason=request.form.get("rejection_reason"),
        )
        return redirect(url_for("html.product_suggestions_admin_page"))

    @blueprint.get("/admin/dashboard")
    @admin_required
    def admin_dashboard():
        """AD04/WEB: exibe métricas do administrador."""
        return render_template(
            "admin_dashboard.html",
            metrics=admin_metrics_service.get_metrics(),
        )

    @blueprint.route("/admin/products/new", methods=["GET", "POST"])
    @admin_required
    def new_product_page():
        """AD01/WEB: cadastra produto pela interface administrativa."""
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

    @blueprint.route("/product-suggestions/new", methods=["GET", "POST"])
    @authenticated_required
    def new_product_suggestion_page():
        """AD05/WEB: permite ao usuário sugerir produto ao admin."""
        if request.method == "POST":
            suggestion_service.suggest_product(
                user_id=session["user_id"],
                name=request.form["name"],
                brand=request.form["brand"],
                price=float(request.form["price"]),
                bar_code=request.form["bar_code"],
                quantity=int(request.form["quantity"]),
            )
            return redirect(url_for("html.products_page"))
        return render_template("new_product_suggestion.html")

    @blueprint.get("/products/<bar_code>/view")
    @authenticated_required
    def product_detail_page(bar_code):
        """US06/WEB: exibe produto e preços observados por loja."""
        product, quantity = product_service.get_product(bar_code)
        return render_template(
            "product_detail.html",
            product=product,
            quantity=quantity,
            price_details=product_price_service.list_product_price_details(bar_code),
            stores=store_service.list_stores(),
        )

    @blueprint.post("/products/<bar_code>/prices/new")
    @authenticated_required
    def new_product_price_page(bar_code):
        """US06/WEB: registra um preço compartilhado pelo usuário."""
        product_price_service.register_price(
            product_bar_code=bar_code,
            store_id=int(request.form["store_id"]),
            user_id=session["user_id"],
            price=float(request.form["price"]),
        )
        return redirect(url_for("html.product_detail_page", bar_code=bar_code))

    @blueprint.get("/cart/view")
    @authenticated_required
    def cart_page():
        """US04/US05/WEB: exibe itens e total do carrinho."""
        items = cart_service.get_items(session.get("cart", {}))
        return render_template(
            "cart.html",
            items=items,
            total=cart_service.calculate_total(items),
        )

    @blueprint.get("/pending-items/view")
    @authenticated_required
    def pending_items_page():
        """US07/WEB: exibe itens não comprados do usuário."""
        return render_template(
            "pending_items.html",
            items=pending_service.list_pending_items(session["user_id"]),
        )

    @blueprint.post("/pending-items/<bar_code>/update/view")
    @authenticated_required
    def update_pending_item_page(bar_code):
        """US07/WEB: atualiza quantidade de pendência."""
        pending_service.update_pending_quantity(
            user_id=session["user_id"],
            bar_code=bar_code,
            quantity=int(request.form["quantity"]),
        )
        return redirect(url_for("html.pending_items_page"))

    @blueprint.post("/pending-items/<bar_code>/remove/view")
    @authenticated_required
    def remove_pending_item_page(bar_code):
        """US07/WEB: resolve uma pendência."""
        pending_service.resolve_pending_item(session["user_id"], bar_code)
        return redirect(url_for("html.pending_items_page"))

    @blueprint.post("/cart/view/items")
    @authenticated_required
    def add_cart_item_page():
        """US04/WEB: adiciona produto ao carrinho pelo formulário."""
        cart = dict(session.get("cart", {}))
        cart_service.add_item(
            cart,
            request.form["bar_code"],
            int(request.form["quantity"]),
        )
        session["cart"] = cart
        return redirect(url_for("html.cart_page"))

    @blueprint.post("/cart/view/items/<bar_code>/update")
    @authenticated_required
    def update_cart_item_page(bar_code):
        """US04/WEB: atualiza a quantidade de um item."""
        cart = dict(session.get("cart", {}))
        cart_service.update_item(cart, bar_code, int(request.form["quantity"]))
        session["cart"] = cart
        return redirect(url_for("html.cart_page"))

    @blueprint.post("/cart/view/items/<bar_code>/remove")
    @authenticated_required
    def remove_cart_item_page(bar_code):
        """US04/WEB: remove um item do carrinho."""
        cart = dict(session.get("cart", {}))
        cart_service.remove_item(cart, bar_code)
        session["cart"] = cart
        return redirect(url_for("html.cart_page"))

    return blueprint


def _start_session(user) -> None:
    """US01/WEB: inicia uma sessão com o usuário autenticado."""
    session.clear()
    session["user_id"] = user.user_id
    session["role"] = user.role


def _optional_float(value: str | None) -> float | None:
    """US06/GPS/WEB: converte campo numérico opcional de formulário.

    Pré-condição: value pode estar vazio ou conter número em texto.
    Pós-condição: retorna float quando preenchido ou None quando ausente.
    """
    if value is None or not value.strip():
        return None
    return float(value)
