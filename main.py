import logging
import os
import time
from datetime import datetime

from curl_cffi import requests

URL = "https://sodoc.embaven.cl/"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TOKEN_NO_CONFIGURADO")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "CHAT_ID_NO_CONFIGURADO")

FRASES_DOMINIO_PARQUEADO = [
    "dynadot.com",
    "website coming soon",
]

FRASES_SITIO_FUNCIONANDO = [
    "Venezuela",
    "Embajada",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("monitor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def enviar_notificacion_telegram(mensaje: str) -> bool:
    if (
        TELEGRAM_TOKEN == "TOKEN_NO_CONFIGURADO"
        or TELEGRAM_CHAT_ID == "CHAT_ID_NO_CONFIGURADO"
    ):
        logger.warning(
            "Telegram no está configurado (faltan TELEGRAM_TOKEN / TELEGRAM_CHAT_ID). "
            "No se pudo enviar la notificación."
        )
        return False

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}

    response = requests.post(api_url, data=payload, timeout=10)
    response.raise_for_status()
    logger.info("Notificación enviada a Telegram correctamente.")
    return True


def verificar_estado(url: str) -> bool:
    headers = {
        "User-Agent": "bruno-runtime/4.0.0",
        "Accept": "application/json, text/plain, */*",
    }
    response = requests.get(url, timeout=15, headers=headers, verify=False)
    if sitio_funcionando(response.text):
        return True
    else:
        return False


def sitio_funcionando(html: str) -> bool:
    if not html:
        return False

    html_lower = html.lower()

    encontrada = any(frase.lower() in html_lower for frase in FRASES_SITIO_FUNCIONANDO)

    for frase in FRASES_DOMINIO_PARQUEADO:
        if frase.lower() in html_lower:
            logger.info(f"Se detectó indicio de dominio parqueado: '{frase}'")
            return False

    return encontrada


if __name__ == "__main__":
    if verificar_estado(URL):
        mensaje = f"Exito: El sitio {URL} está funcionando correctamente."
        logger.info(f"El sitio {URL} está funcionando correctamente.")
        enviar_notificacion_telegram(mensaje)
    else:
        mensaje = f"Fail: El sitio {URL} no está funcionando correctamente."
        logger.warning(mensaje)
