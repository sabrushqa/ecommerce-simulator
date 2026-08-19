FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin ecommerce

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY simulate_ecommerce.py .

USER ecommerce

# Pas de port expose : ce n'est pas un service, c'est un client qui appelle
# l'API REST du switch monetique (SWITCH_BASE_URL) puis se termine une fois
# les scenarios joues.
ENTRYPOINT ["python", "simulate_ecommerce.py"]
