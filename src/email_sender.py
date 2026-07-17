#!/usr/bin/env python3
"""Envío de newsletter por email."""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

logger = logging.getLogger(__name__)


def send_email(newsletter: Dict[str, Any]) -> bool:
    """
    Enviar newsletter por email SMTP.

    Variables de entorno requeridas:
    - SMTP_SERVER
    - SMTP_PORT
    - SMTP_USER
    - SMTP_PASSWORD
    - RECIPIENT_EMAIL
    """

    smtp_server = os.getenv('SMTP_SERVER', '')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    recipient_email = os.getenv('RECIPIENT_EMAIL', '')

    if not all([smtp_server, smtp_user, smtp_password, recipient_email]):
        logger.error("Credenciales SMTP incompletas")
        return False

    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📰 Newsletter Diarios — {newsletter['date']}"
        msg['From'] = smtp_user
        msg['To'] = recipient_email

        # Generar HTML
        html = generate_html(newsletter)

        # Adjuntar parte HTML
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        # Conectar y enviar
        logger.info(f"Conectando a {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email enviado a {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Error de autenticación SMTP")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"Error SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        return False


def generate_html(newsletter: Dict[str, Any]) -> str:
    """Generar HTML del newsletter."""

    date = newsletter.get('date', 'N/A')
    time = newsletter.get('time', 'N/A')
    by_diary = newsletter.get('by_diary', {})
    total = newsletter.get('total_items', 0)

    # Ordenar diarios
    diaries_order = ['El Mercurio', 'La Tercera', 'La Segunda', 'DF']
    sorted_diaries = [d for d in diaries_order if d in by_diary]

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Newsletter Diarios</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 700px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            header {{
                text-align: center;
                border-bottom: 3px solid #667eea;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            h1 {{
                margin: 0;
                color: #667eea;
                font-size: 28px;
            }}
            .meta {{
                color: #999;
                font-size: 14px;
                margin-top: 10px;
            }}
            .diary-section {{
                margin-bottom: 30px;
            }}
            .diary-title {{
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin: 20px 0 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e0e0e0;
            }}
            .news-item {{
                margin-bottom: 15px;
                padding: 12px;
                background: #f9f9f9;
                border-left: 4px solid #667eea;
                border-radius: 4px;
            }}
            .news-item h3 {{
                margin: 0 0 8px;
                font-size: 15px;
                color: #333;
            }}
            .news-item a {{
                color: #667eea;
                text-decoration: none;
            }}
            .news-item a:hover {{
                text-decoration: underline;
            }}
            .news-item .description {{
                color: #666;
                font-size: 13px;
                margin: 8px 0;
            }}
            .news-item .meta {{
                color: #999;
                font-size: 12px;
            }}
            footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
                color: #999;
                font-size: 12px;
            }}
            .stats {{
                text-align: center;
                background: #f0f0f0;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📰 Newsletter Diarios</h1>
                <div class="meta">{date} — {time}</div>
            </header>

            <div class="stats">
                <strong>{total} noticias</strong> recopiladas de 4 medios principales
            </div>
    """

    for diary in sorted_diaries:
        items = by_diary.get(diary, [])
        if not items:
            continue

        html += f'<div class="diary-section">'
        html += f'<div class="diary-title">{diary} ({len(items)})</div>'

        for item in items:
            title = item.get('title', 'Sin título')
            link = item.get('link', '#')
            description = item.get('description', '')

            # Limpiar descripción (remover HTML tags si existen)
            if description:
                from html.parser import HTMLParser
                class MLStripper(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.reset()
                        self.strict = False
                        self.convert_charrefs = True
                        self.text = []
                    def handle_data(self, d):
                        self.text.append(d)
                    def get_data(self):
                        return ''.join(self.text)
                stripper = MLStripper()
                try:
                    stripper.feed(description)
                    description = stripper.get_data()[:150]
                except:
                    pass

            html += f'''
            <div class="news-item">
                <h3><a href="{link}" target="_blank">{title}</a></h3>
            '''
            if description:
                html += f'<div class="description">{description}...</div>'
            html += '</div>'

        html += '</div>'

    html += """
            <footer>
                <p>Newsletter automático generado diariamente.<br>
                Política de privacidad: Las credenciales se almacenan encriptadas y solo se usan para recopilar noticias públicas.</p>
            </footer>
        </div>
    </body>
    </html>
    """

    return html
