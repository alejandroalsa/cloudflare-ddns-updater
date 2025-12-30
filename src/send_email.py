#!/usr/bin/env python3
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# ==============================
# Cargar entorno
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

APP_NAME = os.getenv("APP_NAME", "Cloudflare DDNS Updater")
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM_ADDRESS = os.getenv("MAIL_FROM_ADDRESS", MAIL_USERNAME)
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", APP_NAME)
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")
TEMPLATE_PATH = os.path.join(BASE_DIR, "src", "templates", "email.html")


def send_email(old_ip, new_ip, domains):
    """Envía correo usando la plantilla HTML con los datos de IP y dominios"""
    # Leer la plantilla HTML
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Reemplazar variables
    html_content = html_content.replace("{{old_ip}}", old_ip)
    html_content = html_content.replace("{{new_ip}}", new_ip)
    domains_html = "\n".join([f"<li>{d}</li>" for d in domains])
    html_content = html_content.replace("{{domains_list}}", domains_html)

    # Crear mensaje MIME
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[{APP_NAME}] Cambio de IP detectado"
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM_ADDRESS}>"
    msg["To"] = NOTIFICATION_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    # Conexión SMTP segura
    with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM_ADDRESS, NOTIFICATION_EMAIL, msg.as_string())
