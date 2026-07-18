#!/usr/bin/env python3
"""
Scraper para recopilar noticias de medios chilenos.
Diarios soportados: El Mercurio, La Tercera, La Segunda, DF (Diario Financiero)
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import feedparser
import requests
from bs4 import BeautifulSoup
from email_sender import send_email
from slack_sender import send_to_slack

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def decrypt_credentials(encrypted: str, password: str) -> List[Dict[str, str]]:
    """Desencriptar credenciales (versión simplificada)."""
    try:
        from Crypto.Cipher import AES
        from Crypto.Protocol.KDF import PBKDF2
        import base64

        encrypted_bytes = base64.b64decode(encrypted)
        
        if encrypted_bytes[:8] != b'Salted__':
            raise ValueError("Invalid encrypted format")

        salt = encrypted_bytes[8:16]
        ciphertext = encrypted_bytes[16:]

        key_iv = PBKDF2(password, salt, 48, count=1)
        key = key_iv[:32]
        iv = key_iv[32:48]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        padding_length = plaintext[-1]
        plaintext = plaintext[:-padding_length]

        return json.loads(plaintext.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error desencriptando credenciales: {e}")
        return []


class NewsletterScraper:
    """Scraper para recopilar noticias de los 4 diarios."""

    def __init__(self, credentials: List[Dict[str, str]]):
        self.credentials = {c['diary']: c for c in credentials}
        self.news_items = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def scrape_all(self) -> Dict[str, Any]:
        """Ejecutar scraping de todos los diarios."""
        logger.info("Iniciando scraping de noticias...")

        self.scrape_mercurio()
        self.scrape_tercera()
        self.scrape_segunda()
        self.scrape_df()

        logger.info(f"Total de noticias recopiladas: {len(self.news_items)}")
        return self.generate_newsletter()

    def scrape_mercurio(self):
        """El Mercurio - RSS disponible públicamente."""
        try:
            logger.info("Scrapeando El Mercurio...")
            url = "https://www.elmercurio.com/rss"
            feed = feedparser.parse(url)

            count = 0
            for entry in feed.entries[:10]:
                self.news_items.append({
                    'diary': 'El Mercurio',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
                count += 1
            logger.info(f"El Mercurio: {count} noticias")
        except Exception as e:
            logger.error(f"Error en El Mercurio: {e}")

    def scrape_tercera(self):
        """La Tercera - RSS con suscripción, fallback a web."""
        try:
            logger.info("Scrapeando La Tercera...")
            url = "https://www.latercera.com/rss"
            feed = feedparser.parse(url)

            count = 0
            for entry in feed.entries[:10]:
                self.news_items.append({
                    'diary': 'La Tercera',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
                count += 1
            logger.info(f"La Tercera: {count} noticias")
        except Exception as e:
            logger.error(f"Error en La Tercera: {e}")

    def scrape_segunda(self):
        """La Segunda - Web scraping (sin RSS directo)."""
        try:
            logger.info("Scrapeando La Segunda...")
            url = "https://www.lasegunda.com"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('article', limit=10)

            count = 0
            for article in articles:
                title_elem = article.find('h2') or article.find('h3')
                link_elem = article.find('a', href=True)

                if title_elem and link_elem:
                    self.news_items.append({
                        'diary': 'La Segunda',
                        'title': title_elem.get_text().strip(),
                        'description': '',
                        'link': link_elem.get('href', ''),
                        'published': '',
                        'timestamp': datetime.now().isoformat()
                    })
                    count += 1

            logger.info(f"La Segunda: {count} noticias")
        except Exception as e:
            logger.error(f"Error en La Segunda: {e}")

    def scrape_df(self):
        """DF (Diario Financiero) - RSS."""
        try:
            logger.info("Scrapeando DF...")
            url = "https://www.df.cl/rss"
            feed = feedparser.parse(url)

            count = 0
            for entry in feed.entries[:10]:
                self.news_items.append({
                    'diary': 'DF',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
                count += 1
            logger.info(f"DF: {count} noticias")
        except Exception as e:
            logger.error(f"Error en DF: {e}")

    def generate_newsletter(self) -> Dict[str, Any]:
        """Generar estructura del newsletter."""
        by_diary = {}
        for item in self.news_items:
            diary = item['diary']
            if diary not in by_diary:
                by_diary[diary] = []
            by_diary[diary].append(item)

        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'by_diary': by_diary,
            'total_items': len(self.news_items),
            'raw_items': self.news_items
        }


def main():
    """Función principal."""
    encrypted_creds = os.getenv('CREDENTIALS_ENCRYPTED', '')
    encryption_password = os.getenv('ENCRYPTION_PASSWORD', '')

    if not encrypted_creds or not encryption_password:
        logger.error("CREDENTIALS_ENCRYPTED o ENCRYPTION_PASSWORD no configurados")
        return False

    logger.info("Desencriptando credenciales...")
    try:
        credentials = decrypt_credentials(encrypted_creds, encryption_password)
        if not credentials:
            logger.error("No se pudieron desencriptar las credenciales")
            return False
    except Exception as e:
        logger.error(f"Error desencriptando: {e}")
        return False

    scraper = NewsletterScraper(credentials)
    newsletter = scraper.scrape_all()

    if newsletter['total_items'] == 0:
        logger.warning("No se recopilaron noticias")

    success = True
    try:
        send_email(newsletter)
        logger.info("Newsletter enviado por email")
    except Exception as e:
        logger.error(f"Error enviando email: {e}")
        success = False

    try:
        send_to_slack(newsletter)
        logger.info("Newsletter enviado a Slack")
    except Exception as e:
        logger.error(f"Error enviando a Slack: {e}")
        success = False

    return success


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
