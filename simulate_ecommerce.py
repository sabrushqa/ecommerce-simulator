"""
Simule des sites/applications e-commerce qui appellent l'API REST du switch monetique
(canal ECOMMERCE, voir docs/scenarios.md scenarios 14 a 18).

Contrairement au canal TPE (ISO 8583/TCP), un site e-commerce appelle simplement
l'API REST du switch, comme une vraie integration avec une passerelle de paiement.
"""

import os
import hashlib
import hmac
import time
import uuid
import requests

SWITCH_BASE_URL = os.environ.get("SWITCH_BASE_URL", "http://localhost:8090")
ENDPOINT = f"{SWITCH_BASE_URL}/api/ecommerce/transactions"
MONETIQUE_INTERNAL_TOKEN = os.environ.get(
    "MONETIQUE_INTERNAL_TOKEN", "change-me-monetique-internal-token"
)
MONETIQUE_SIGNATURE_SECRET = os.environ.get(
    "MONETIQUE_SIGNATURE_SECRET", "change-me-monetique-signature-secret-32chars"
)

SCENARIOS = [
    {
        "nom": "Paiement 3D Secure reussi",
        "payload": {
            "idSiteEcommerce": "SITE_LANACASH_SHOP",
            "idCommercant": "COM0001",
            "montant": 249.90,
            "typeTransaction": "ACHAT",
            "authentification3dsReussie": True,
        },
    },
    {
        "nom": "3D Secure echoue",
        "payload": {
            "idSiteEcommerce": "SITE_LANACASH_SHOP",
            "idCommercant": "COM0001",
            "montant": 89.00,
            "typeTransaction": "ACHAT",
            "authentification3dsReussie": False,
        },
    },
    {
        "nom": "Remboursement e-commerce",
        "payload": {
            "idSiteEcommerce": "SITE_LANACASH_SHOP",
            "idCommercant": "COM0001",
            "montant": 249.90,
            "typeTransaction": "REMBOURSEMENT",
            "authentification3dsReussie": True,
        },
    },
]


def executer_scenario(scenario: dict) -> None:
    print(f"=== Scenario : {scenario['nom']} ===")
    timestamp = str(int(time.time()))
    request_id = str(uuid.uuid4())
    path = "/api/ecommerce/transactions"
    canonical = f"{timestamp}.{request_id}.POST.{path}"
    signature = hmac.new(
        MONETIQUE_SIGNATURE_SECRET.encode(), canonical.encode(), hashlib.sha256
    ).hexdigest()
    response = requests.post(
        ENDPOINT,
        json=scenario["payload"],
        headers={
            "X-Monetique-Token": MONETIQUE_INTERNAL_TOKEN,
            "X-Monetique-Timestamp": timestamp,
            "X-Monetique-Request-Id": request_id,
            "X-Monetique-Signature": signature,
        },
        timeout=10,
    )
    print(f"HTTP {response.status_code} -> {response.json()}")


if __name__ == "__main__":  # pragma: no cover - point d'entree CLI, couvert via executer_scenario()
    for scenario in SCENARIOS:
        executer_scenario(scenario)
