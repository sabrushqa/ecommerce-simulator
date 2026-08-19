# ecommerce-simulator

Simule des sites/applications e-commerce qui appellent l'API REST du
[switch monétique](https://github.com/sabrushqa/switch_monetique-) (canal
ECOMMERCE, requêtes REST signées HMAC — voir `InternalApiTokenFilter` /
`MonetiqueSignatureService` côté switch).

Contrairement au canal TPE (ISO 8583/TCP, voir
[tpe-simulator](https://github.com/sabrushqa/tpe-simulator)), un site e-commerce
appelle simplement l'API REST du switch, comme une vraie intégration avec une
passerelle de paiement.

## Utilisation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

export SWITCH_BASE_URL=http://localhost:8090
export MONETIQUE_INTERNAL_TOKEN=...
export MONETIQUE_SIGNATURE_SECRET=...
python simulate_ecommerce.py

pytest --cov=simulate_ecommerce --cov-report=term-missing
```

Couverture actuelle : 100 % (9 tests, `requests.post` mocké — aucun appel
réseau réel dans les tests).
