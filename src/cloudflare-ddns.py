#!/usr/bin/env python3
import os
import time
import json
import requests
import logging
from dotenv import load_dotenv
import sys

# ==============================
# Cargar entorno
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 300))
PUBLIC_IP_SERVICE = os.getenv("PUBLIC_IP_SERVICE")
CONFIG_JSON = os.getenv("CONFIG_JSON")
LOG_FILE = os.getenv("LOG_FILE", "/var/log/cloudflare-ddns.log")

# ==============================
# Logging configurado
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

# ==============================
# Funciones
# ==============================
def get_public_ip():
    """Obtiene la IP pública desde el servicio definido en .env o IP de debug si APP_DEBUG=True"""
    app_debug = os.getenv("APP_DEBUG", "false").lower() == "true"

    if app_debug:
        debug_ip = os.getenv("DEBUG_IP")
        if not debug_ip:
            raise ValueError("APP_DEBUG está activado pero no se ha definido DEBUG_IP en .env")
        logging.info(f"[DEBUG] Usando IP de depuración: {debug_ip}")
        return debug_ip

    r = requests.get(PUBLIC_IP_SERVICE, timeout=10)
    r.raise_for_status()
    return r.text.strip()


def get_dns_records(zone_id, token):
    """Obtiene todos los registros DNS de una zona"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["result"]


def update_dns_record(zone_id, record, new_ip, token):
    """
    Actualiza un registro tipo A con la nueva IP,
    respetando proxied y TTL actuales.
    """
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record['id']}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": record["name"],
        "content": new_ip,
        "ttl": record["ttl"],
        "proxied": record["proxied"]
    }
    r = requests.put(url, headers=headers, json=payload)
    r.raise_for_status()
    logging.info(f"[{zone_id}] {record['name']} actualizado a {new_ip}")

def check_log_size():
    """Vacía el log si supera el tamaño máximo definido en LOG_MAX_SIZE_KB"""
    try:
        max_size_kb = int(os.getenv("LOG_MAX_SIZE_KB", 500))
        if os.path.exists(LOG_FILE):
            size_kb = os.path.getsize(LOG_FILE) / 1024
            if size_kb >= max_size_kb:
                with open(LOG_FILE, "w") as f:
                    f.write("")  # vaciar archivo
                logging.info(f"Log limpiado automáticamente (superó {max_size_kb} KB)")
    except Exception as e:
        logging.error(f"No se pudo verificar o limpiar el log: {e}")


# ==============================
# Main loop
# ==============================
def main():
    logging.info("Cloudflare DDNS iniciado")

    with open(CONFIG_JSON) as f:
        config = json.load(f)

    last_ip = None

    while True:
        try:
            check_log_size()

            current_ip = get_public_ip()

            if current_ip != last_ip:
                logging.info(f"IP detectada: {current_ip}")
                updated_domains = []

                # Recorremos todos los dominios de config.json
                for domain, data in config["domains"].items():
                    token = data["api_token"]
                    zone_id = data["zone_id"]
                    records_to_update = data["records"]

                    # Obtenemos todos los registros de la zona
                    dns_records = get_dns_records(zone_id, token)

                    for record in dns_records:
                        # Solo tipo A y listado en records_to_update
                        if record["type"] != "A":
                            continue

                        record_name = record["name"]
                        for target in records_to_update:
                            if target == record_name or f"{target}.{domain}" == record_name:
                                if record["content"] != current_ip:
                                    update_dns_record(zone_id, record, current_ip, token)
                                    updated_domains.append(record_name)
                                break

                # Enviar correo después de actualizar todos los registros
                if updated_domains:
                    try:
                        from send_email import send_email
                        send_email(
                            old_ip=last_ip or "N/A",
                            new_ip=current_ip,
                            domains=updated_domains
                        )
                        logging.info(f"Correo de notificación enviado a {os.getenv('NOTIFICATION_EMAIL')}")
                    except Exception as e:
                        logging.error(f"No se pudo enviar el correo: {e}")

                # Actualizamos la IP última después de todo
                last_ip = current_ip
            else:
                logging.info("IP sin cambios")

        except Exception as e:
            logging.error(f"Error: {e}")

        time.sleep(UPDATE_INTERVAL)

# Ejecutar directamente
if __name__ == "__main__":
    main()
