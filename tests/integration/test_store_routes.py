import sqlite3
import unittest

from app.web.app import create_app


class TestUS06StoreRoutes(unittest.TestCase):
    """US06: testa cadastro e consulta HTTP de locais de compra."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.app = create_app(self.connection)
        self.client = self.app.test_client()

    def tearDown(self):
        self.connection.close()

    def authenticate_as(self, role, user_id=1):
        """US06: configura uma sessão autenticada para o teste."""
        with self.client.session_transaction() as flask_session:
            flask_session["user_id"] = user_id
            flask_session["role"] = role

    def test_us06_admin_creates_store(self):
        """US06: admin deve cadastrar local válido e receber HTTP 201."""
        self.authenticate_as("admin")

        response = self.client.post(
            "/stores",
            json={
                "name": "Mercado Central",
                "address": "Rua Principal, 100",
                "observation": "Aberto aos domingos",
                "latitude": -15.793889,
                "longitude": -47.882778,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json(),
            {
                "id": 1,
                "name": "Mercado Central",
                "address": "Rua Principal, 100",
                "observation": "Aberto aos domingos",
                "latitude": -15.793889,
                "longitude": -47.882778,
            },
        )

    def test_us06_reject_invalid_store_route(self):
        """US06: dados inválidos devem retornar HTTP 400."""
        self.authenticate_as("admin")

        response = self.client.post(
            "/stores",
            json={
                "name": "",
                "address": "Rua Principal, 100",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_us06_common_user_lists_stores(self):
        """US06: usuário autenticado deve listar locais cadastrados."""
        self.authenticate_as("admin")
        self.client.post(
            "/stores",
            json={
                "name": "Mercado Central",
                "address": "Rua Principal, 100",
                "latitude": -15.793889,
                "longitude": -47.882778,
            },
        )
        self.authenticate_as("user", user_id=7)

        response = self.client.get("/stores")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["name"], "Mercado Central")

    def test_us06_gps_authenticated_user_finds_nearest_store(self):
        """US06/GPS: usuário autenticado deve buscar a loja mais próxima."""
        self.authenticate_as("admin")
        self.client.post(
            "/stores",
            json={
                "name": "Mercado Distante",
                "address": "Taguatinga",
                "latitude": -15.832,
                "longitude": -48.057,
            },
        )
        self.client.post(
            "/stores",
            json={
                "name": "Mercado Próximo",
                "address": "Asa Sul",
                "latitude": -15.794,
                "longitude": -47.883,
            },
        )
        self.authenticate_as("user", user_id=7)

        response = self.client.get(
            "/stores/nearest?latitude=-15.793889&longitude=-47.882778"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["store"]["name"], "Mercado Próximo")
        self.assertLess(payload["distance_km"], 1)

    def test_us06_gps_reject_unauthenticated_nearest_store_route(self):
        """US06/GPS: visitante não deve buscar loja mais próxima."""
        response = self.client.get(
            "/stores/nearest?latitude=-15.793889&longitude=-47.882778"
        )

        self.assertEqual(response.status_code, 401)

    def test_us06_reject_common_user_store_creation(self):
        """US06: usuário comum não deve cadastrar local."""
        self.authenticate_as("user")

        response = self.client.post(
            "/stores",
            json={
                "name": "Mercado Central",
                "address": "Rua Principal, 100",
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_us06_reject_unauthenticated_store_listing(self):
        """US06: visitante não deve listar locais."""
        response = self.client.get("/stores")

        self.assertEqual(response.status_code, 401)
