#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from slack_sender import send_to_slack

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsletterScraper:
    def __init__(self, credentials):
        self.credentials = {c['diary']: c for c in credentials}
        self.news_items = []
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

    def scrape_all(self):
        logger.info("Iniciando scraping...")
        self.scrape_mercurio()
        self.scrape_tercera()
        self.scrape_segunda()
        self.scrape_df()
        self.scrape_biobiochile()
        self.scrape_cnnchile()
        logger.info(f"Total: {len(self.news_items)} noticias")
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'by_diary': self._organize_by_diary(),
            'total_items': len(self.news_items),
            'raw_items': self.news_items
        }

    def _organize_by_diary(self):
        by_diary = {}
        for item in self.news_items:
            diary = item['diary']
            if diary not in by_diary:
                by_diary[diary] = []
            by_diary[diary].append(item)
        return by_diary

    def _login_mercurio(self):
        """Intenta hacer login en El Mercurio"""
        try:
            creds = self.credentials.get('El Mercurio', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en El Mercurio...")
            login_url = "https://www.elmercurio.com/login"
            payload = {
                'email': creds.get('user', ''),
                'password': creds.get('password', '')
            }
            response = self.session.post(login_url, data=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Login El Mercurio fallido: {e}")
            return False

    def scrape_mercurio(self):
        try:
            logger.info("El Mercurio...")
            self._login_mercurio()

            feed = feedparser.parse("https://www.elmercurio.com/rss")
            for entry in feed.entries[:10]:
                self.news_items.append({
                    'diary': 'El Mercurio',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
            logger.info(f"El Mercurio: {len(feed.entries[:10])} noticias")
        except Exception as e:
            logger.error(f"El Mercurio: {e}")

    def _login_tercera(self):
        """Intenta hacer login en La Tercera"""
        try:
            creds = self.credentials.get('La Tercera', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en La Tercera...")
            login_url = "https://www.latercera.com/auth/login"
            payload = {
                'email': creds.get('user', ''),
                'password': creds.get('password', '')
            }
            response = self.session.post(login_url, data=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Login La Tercera fallido: {e}")
            return False

    def scrape_tercera(self):
        try:
            logger.info("La Tercera...")
            self._login_tercera()

            feed = feedparser.parse("https://www.latercera.com/rss")
            for entry in feed.entries[:10]:
                self.news_items.append({
                    'diary': 'La Tercera',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
            logger.info(f"La Tercera: {len(feed.entries[:10])} noticias")
        except Exception as e:
            logger.error(f"La Tercera: {e}")

    def _login_segunda(self):
        """Intenta hacer login en La Segunda"""
        try:
            creds = self.credentials.get('La Segunda', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en La Segunda...")
            login_url = "https://www.lasegunda.com/login"
            payload = {
                'email': creds.get('user', ''),
                'password': creds.get('password', '')
            }
            response = self.session.post(login_url, data=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Login La Segunda fallido: {e}")
            return False

    def scrape_segunda(self):
        try:
            logger.info("La Segunda...")
            self._login_segunda()

            response = self.session.get("https://www.lasegunda.com", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', limit=10)
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
            logger.info(f"La Segunda: {len(articles)} noticias")
        except Exception as e:
            logger.error(f"La Segunda: {e}")

    def _login_df(self):
        """Intenta hacer login en DF"""
        try:
            creds = self.credentials.get('DF', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en DF...")
            login_url = "https://www.df.cl/login"
            payload = {
                'email': creds.get('user', ''),
                'password': creds.get('password', '')
            }
            response = self.session.post(login_url, data=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Login DF fallido: {e}")
            return False

    def scrape_df(self):
        try:
            logger.info("DF...")
            self._login_df()

            feed = feedparser.parse("https://www.df.cl/rss")
            for entry in feed.entries[:10]:
                self.news_items.append({
                    'diary': 'DF',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
            logger.info(f"DF: {len(feed.entries[:10])} noticias")
        except Exception as e:
            logger.error(f"DF: {e}")

    def scrape_biobiochile(self):
        try:
            logger.info("BioBioChile...")
            feed = feedparser.parse("https://www.biobiochile.cl/rss/")
            for entry in feed.entries[:8]:
                self.news_items.append({
                    'diary': 'BioBioChile',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
            logger.info(f"BioBioChile: {len(feed.entries[:8])} noticias")
        except Exception as e:
            logger.error(f"BioBioChile: {e}")

    def scrape_cnnchile(self):
        try:
            logger.info("CNN Chile...")
            feed = feedparser.parse("https://www.cnnchile.com/feed/rss/")
            for entry in feed.entries[:8]:
                self.news_items.append({
                    'diary': 'CNN Chile',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
            logger.info(f"CNN Chile: {len(feed.entries[:8])} noticias")
        except Exception as e:
            logger.error(f"CNN Chile: {e}")

def save_news_to_json(newsletter, output_file='web/data/news.json'):
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        existing_data = []
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        new_data = existing_data + newsletter['raw_items']
        new_data = new_data[-500:]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Noticias guardadas: {len(new_data)} total")
        return True
    except Exception as e:
        logger.error(f"Error guardando noticias: {e}")
        return False

def main():
    credentials_json = os.getenv('CREDENTIALS_JSON', '')

    if not credentials_json:
        logger.error("CREDENTIALS_JSON no configurado")
        return False

    try:
        credentials = json.loads(credentials_json)
        logger.info(f"Credenciales cargadas: {len(credentials)} diarios")
    except Exception as e:
        logger.error(f"Error parsing CREDENTIALS_JSON: {e}")
        return False

    scraper = NewsletterScraper(credentials)
    newsletter = scraper.scrape_all()
    save_news_to_json(newsletter)

    try:
        send_to_slack(newsletter)
        logger.info("Newsletter enviado a Slack ✅")
        return True
    except Exception as e:
        logger.error(f"Error Slack: {e}")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
