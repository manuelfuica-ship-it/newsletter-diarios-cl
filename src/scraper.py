#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from email_sender import send_email
from slack_sender import send_to_slack

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsletterScraper:
    def __init__(self, credentials):
        self.credentials = {c['diary']: c for c in credentials}
        self.news_items = []
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})

    def scrape_all(self):
        logger.info("Iniciando scraping...")
        self.scrape_mercurio()
        self.scrape_tercera()
        self.scrape_segunda()
        self.scrape_df()
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

    def scrape_mercurio(self):
        try:
            logger.info("El Mercurio...")
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

    def scrape_tercera(self):
        try:
            logger.info("La Tercera...")
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

    def scrape_segunda(self):
        try:
            logger.info("La Segunda...")
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

    def scrape_df(self):
        try:
            logger.info("DF...")
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

def main():
    credentials_json = os.getenv('CREDENTIALS_JSON', '')
    
    if not credentials_json:
        logger.error("CREDENTIALS_JSON no configurado")
        return False

    try:
        credentials = json.loads(credentials_json)
        logger.info(f"Credenciales cargadas: {len(credentials)} diarios")
    except Exception as e:
        logger.error(f"Error parsando credenciales: {e}")
        return False

    scraper = NewsletterScraper(credentials)
    newsletter = scraper.scrape_all()

    success = True
    try:
        send_email(newsletter)
        logger.info("Email enviado")
    except Exception as e:
        logger.error(f"Error email: {e}")
        success = False

    try:
        send_to_slack(newsletter)
        logger.info("Slack enviado")
    except Exception as e:
        logger.error(f"Error Slack: {e}")
        success = False

    return success

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
