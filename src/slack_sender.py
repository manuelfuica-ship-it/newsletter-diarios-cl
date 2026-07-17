#!/usr/bin/env python3
"""Envío de newsletter a Slack."""

import os
import logging
import json
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


def send_to_slack(newsletter: Dict[str, Any]) -> bool:
    """
    Enviar newsletter a Slack usando Incoming Webhook.

    Variables de entorno requeridas:
    - SLACK_WEBHOOK_URL
    """

    webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')

    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL no configurada")
        return False

    try:
        payload = generate_slack_payload(newsletter)

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            logger.info("Mensaje enviado a Slack")
            return True
        else:
            logger.error(f"Error Slack (HTTP {response.status_code}): {response.text}")
            return False

    except requests.RequestException as e:
        logger.error(f"Error enviando a Slack: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return False


def generate_slack_payload(newsletter: Dict[str, Any]) -> Dict[str, Any]:
    """Generar payload para Slack."""

    date = newsletter.get('date', 'N/A')
    time = newsletter.get('time', 'N/A')
    by_diary = newsletter.get('by_diary', {})
    total = newsletter.get('total_items', 0)

    # Ordenar diarios
    diaries_order = ['El Mercurio', 'La Tercera', 'La Segunda', 'DF']
    sorted_diaries = [d for d in diaries_order if d in by_diary]

    # Construir bloques para Slack
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📰 Newsletter Diarios",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{date}* • {total} noticias recopiladas"
            }
        },
        {
            "type": "divider"
        }
    ]

    # Agregar noticias por diario
    for diary in sorted_diaries:
        items = by_diary.get(diary, [])
        if not items:
            continue

        # Título del diario
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{diary}* ({len(items)} noticias)"
            }
        })

        # Agregar hasta 5 noticias por diario en Slack (limitar para no saturar)
        for item in items[:5]:
            title = item.get('title', 'Sin título')
            link = item.get('link', '#')
            description = item.get('description', '')

            # Limpiar descripción
            if description:
                # Remover HTML tags básicamente
                import re
                description = re.sub(r'<[^>]+>', '', description)
                description = description[:100].strip()

            text = f"<{link}|{title}>"
            if description:
                text += f"\n_{description}_"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            })

        blocks.append({"type": "divider"})

    # Remover último divider
    if blocks and blocks[-1].get("type") == "divider":
        blocks.pop()

    # Footer
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Generado automáticamente • {time}"
            }
        ]
    })

    return {
        "blocks": blocks,
        "text": f"Newsletter Diarios — {date}"
    }
