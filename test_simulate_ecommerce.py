"""
Tests de simulate_ecommerce.py : verifie que chaque scenario envoie bien la
requete signee (HMAC) attendue par switch-monetique-service (voir
InternalApiTokenFilter/MonetiqueSignatureService cote switch) - pas d'appel
reseau reel, requests.post est mocke.
"""

import hashlib
import hmac
import uuid
from unittest.mock import MagicMock, patch

import pytest

import simulate_ecommerce as sim


def expected_signature(timestamp: str, request_id: str, method: str, path: str) -> str:
    canonical = f"{timestamp}.{request_id}.{method}.{path}"
    return hmac.new(
        sim.MONETIQUE_SIGNATURE_SECRET.encode(), canonical.encode(), hashlib.sha256
    ).hexdigest()


def make_mock_response(status_code=200, body=None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = body or {"statut": "ACCEPTE"}
    return response


class TestExecuterScenario:
    @patch("simulate_ecommerce.requests.post")
    def test_appelle_le_bon_endpoint_avec_le_payload_du_scenario(self, mock_post):
        mock_post.return_value = make_mock_response()

        sim.executer_scenario(sim.SCENARIOS[0])

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == sim.ENDPOINT
        assert kwargs["json"] == sim.SCENARIOS[0]["payload"]
        assert kwargs["timeout"] == 10

    @patch("simulate_ecommerce.requests.post")
    def test_envoie_le_token_interne_dans_les_headers(self, mock_post):
        mock_post.return_value = make_mock_response()

        sim.executer_scenario(sim.SCENARIOS[0])

        headers = mock_post.call_args.kwargs["headers"]
        assert headers["X-Monetique-Token"] == sim.MONETIQUE_INTERNAL_TOKEN

    @patch("simulate_ecommerce.requests.post")
    def test_le_request_id_est_un_uuid_valide(self, mock_post):
        mock_post.return_value = make_mock_response()

        sim.executer_scenario(sim.SCENARIOS[0])

        headers = mock_post.call_args.kwargs["headers"]
        # Leve ValueError si ce n'est pas un UUID valide - la simple absence
        # d'exception constitue l'assertion.
        uuid.UUID(headers["X-Monetique-Request-Id"])

    @patch("simulate_ecommerce.requests.post")
    def test_la_signature_correspond_exactement_a_celle_attendue_par_le_switch(self, mock_post):
        mock_post.return_value = make_mock_response()

        sim.executer_scenario(sim.SCENARIOS[0])

        headers = mock_post.call_args.kwargs["headers"]
        recomputed = expected_signature(
            headers["X-Monetique-Timestamp"],
            headers["X-Monetique-Request-Id"],
            "POST",
            "/api/ecommerce/transactions",
        )
        assert headers["X-Monetique-Signature"] == recomputed

    @patch("simulate_ecommerce.requests.post")
    def test_deux_appels_successifs_utilisent_des_request_id_distincts(self, mock_post):
        mock_post.return_value = make_mock_response()

        sim.executer_scenario(sim.SCENARIOS[0])
        first_request_id = mock_post.call_args.kwargs["headers"]["X-Monetique-Request-Id"]

        sim.executer_scenario(sim.SCENARIOS[0])
        second_request_id = mock_post.call_args.kwargs["headers"]["X-Monetique-Request-Id"]

        assert first_request_id != second_request_id

    @patch("simulate_ecommerce.requests.post")
    def test_affiche_le_nom_du_scenario_et_le_statut_http(self, mock_post, capsys):
        mock_post.return_value = make_mock_response(status_code=200, body={"statut": "ACCEPTE"})

        sim.executer_scenario(sim.SCENARIOS[0])

        output = capsys.readouterr().out
        assert "Paiement 3D Secure reussi" in output
        assert "HTTP 200" in output
        assert "ACCEPTE" in output

    @pytest.mark.parametrize("scenario", sim.SCENARIOS, ids=lambda s: s["nom"])
    @patch("simulate_ecommerce.requests.post")
    def test_chaque_scenario_predefini_sexecute_sans_erreur(self, mock_post, scenario):
        mock_post.return_value = make_mock_response()

        sim.executer_scenario(scenario)

        mock_post.assert_called_once()
        assert mock_post.call_args.kwargs["json"] == scenario["payload"]
