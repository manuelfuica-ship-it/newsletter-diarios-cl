#!/usr/bin/env python3
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_email(newsletter):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '465'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    recipient_email = os.getenv('RECIPIENT_EMAIL', '')

    if not all([smtp_user, smtp_password, recipient_email]):
        logger.error("Credenciales SMTP incompletas")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"📰 Newsletter Diarios — {newsletter['date']}"
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg.attach(MIMEText(generate_html(newsletter), 'html', 'utf-8'))

        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email enviado a {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Error email: {e}")
        return False

def generate_html(newsletter):
    date = newsletter.get('date', 'N/A')
    by_diary = newsletter.get('by_diary', {})
    total = newsletter.get('total_items', 0)
    diaries_order = ['El Mercurio', 'La Tercera', 'La Segunda', 'DF']
    sorted_diaries = [d for d in diaries_order if d in by_diary]

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .container {{ background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            header {{ text-align: center; border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }}
            h1 {{ margin: 0; color: #667eea; }}
            .diary-section {{ margin-bottom: 30px; }}
            .diary-title {{ font-size: 18px; font-weight: bold; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-bottom: 15px; }}
            .news-item {{ margin-bottom: 15px; padding: 12px; background: #f9f9f9; border-left: 4px solid #667eea; }}
            .news-item h3 {{ margin: 0 0 8px; font-size: 15px; }}
            .news-item a {{ color: #667eea; text-decoration: none; }}
            .news-item a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📰 Newsletter Diarios</h1>
                <p style="color: #999; margin-top: 10px;">{date} • {total} noticias</p>
            </header>
    """

    for diary in sorted_diaries:
        items = by_diary.get(diary, [])
        if not items:
            continue
        html += f'<div class="diary-section"><div class="diary-title">{diary} ({len(items)})</div>'
        for item in items:
            title = item.get('title', 'Sin título')
            link = item.get('link', '#')
            html += f'<div class="news-item"><h3><a href="{link}" target="_blank">{title}</a></h3></div>'
        html += '</div>'

    html += """
        </div>
    </body>
    </html>
    """
    return html
