#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from slack_sender import send_to_slack

try:
    from selenium_scraper import SeleniumScraper
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

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

    def extract_summary(self, url, max_chars=1500):
        """Extrae un resumen más largo de un artículo (primeros párrafos)"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remover scripts y styles
            for script in soup(["script", "style"]):
                script.decompose()

            # Estrategia 1: Buscar article/main
            article = soup.find(['article', 'main'])
            if not article:
                # Estrategia 2: Buscar div con content/body
                article = soup.find('div', class_=lambda x: x and any(kw in str(x).lower() for kw in ['content', 'body', 'article', 'post']))
            if not article:
                # Estrategia 3: Usar body completo
                article = soup.body

            if article:
                # Extraer TODOS los párrafos sin limite mínimo
                paragraphs = article.find_all('p', limit=15)
                summary_parts = []
                total_chars = 0

                for p in paragraphs:
                    text = p.get_text().strip()
                    # Aceptar párrafos de cualquier tamaño (menos de 10 chars probablemente sean basura)
                    if text and len(text) > 10:
                        if total_chars + len(text) < max_chars:
                            summary_parts.append(text)
                            total_chars += len(text) + 2
                        else:
                            break

                if summary_parts:
                    summary = '\n\n'.join(summary_parts)
                    if len(summary) > 200:  # Reducir threshold
                        return summary

                # Si no hay párrafos, intentar extraer divs con texto
                if not summary_parts:
                    divs = article.find_all(['div', 'section'], limit=10)
                    for div in divs:
                        text = div.get_text().strip()
                        if text and len(text) > 100:
                            return text[:max_chars]
        except Exception as e:
            logger.debug(f"Error extrayendo resumen de {url}: {e}")
        return None

    def _login_mercurio(self):
        """Intenta hacer login en El Mercurio"""
        try:
            creds = self.credentials.get('mercurio', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en El Mercurio...")
            login_url = "https://www.elmercurio.com/login"
            payload = {
                'email': creds.get('username', ''),
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

            # Intentar con Selenium si está disponible
            if SELENIUM_AVAILABLE:
                creds = self.credentials.get('mercurio', {})
                if creds:
                    selenium_scraper = SeleniumScraper()
                    selenium_articles = selenium_scraper.scrape_mercurio_with_selenium(
                        creds.get('username', ''),
                        creds.get('password', '')
                    )
                    if selenium_articles:
                        self.news_items.extend(selenium_articles)
                        logger.info(f"El Mercurio (Selenium): {len(selenium_articles)} noticias")
                        return

            # Fallback: extraer TODOS los links y filtrar por noticias
            self._login_mercurio()
            response = self.session.get("https://www.elmercurio.com", timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar todos los links que parecen noticias
            all_links = soup.find_all('a', href=True)
            seen_titles = set()
            count = 0

            for link_elem in all_links:
                try:
                    link = link_elem.get('href', '').strip()
                    title = link_elem.get_text().strip()

                    # Filtrar por URL que parecen noticias y títulos decentes
                    if (title and len(title) > 10 and len(title) < 200 and
                        ('/noticia/' in link or '/articulo/' in link or link.startswith('/')) and
                        title not in seen_titles):

                        seen_titles.add(title)
                        full_link = link if link.startswith('http') else f"https://www.elmercurio.com{link}"
                        description = self.extract_summary(full_link)

                        if not description or len(description) < 100:
                            description = f"{title}\n\n[Haz clic en 'Leer más' para ver el artículo completo en El Mercurio]"

                        self.news_items.append({
                            'diary': 'El Mercurio',
                            'title': title,
                            'description': description,
                            'link': full_link,
                            'published': '',
                            'timestamp': datetime.now().isoformat()
                        })
                        count += 1
                        if count >= 15:
                            break
                except:
                    pass

            logger.info(f"El Mercurio: {count} noticias")
        except Exception as e:
            logger.error(f"El Mercurio: {e}")

    def _login_tercera(self):
        """Intenta hacer login en La Tercera"""
        try:
            creds = self.credentials.get('tercera', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en La Tercera...")
            login_url = "https://www.latercera.com/auth/login"
            payload = {
                'email': creds.get('username', ''),
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
            for entry in feed.entries[:30]:
                self.news_items.append({
                    'diary': 'La Tercera',
                    'title': entry.get('title', 'Sin título'),
                    'description': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'timestamp': datetime.now().isoformat()
                })
            logger.info(f"La Tercera: {len(feed.entries[:30])} noticias")
        except Exception as e:
            logger.error(f"La Tercera: {e}")

    def _login_segunda(self):
        """Intenta hacer login en La Segunda"""
        try:
            creds = self.credentials.get('segunda', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en La Segunda...")
            login_url = "https://www.lasegunda.com/login"
            payload = {
                'email': creds.get('username', ''),
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

            # Intentar con Selenium si está disponible
            if SELENIUM_AVAILABLE:
                creds = self.credentials.get('segunda', {})
                if creds:
                    selenium_scraper = SeleniumScraper()
                    selenium_articles = selenium_scraper.scrape_segunda_with_selenium(
                        creds.get('username', ''),
                        creds.get('password', '')
                    )
                    if selenium_articles:
                        self.news_items.extend(selenium_articles)
                        logger.info(f"La Segunda (Selenium): {len(selenium_articles)} noticias")
                        return

            # Fallback mejorado con resúmenes más largos
            self._login_segunda()
            response = self.session.get("https://www.lasegunda.com", timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = soup.find_all('article', limit=20)
            if not articles:
                articles = soup.find_all(['div', 'li'], class_=lambda x: x and 'item' in x.lower(), limit=20)

            count = 0
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a', href=True)
                    link = link_elem.get('href', '') if link_elem else ''

                    if title_elem and link:
                        title = title_elem.get_text().strip()
                        if len(title) > 5:
                            # Extraer resumen más largo
                            full_link = link if link.startswith('http') else f"https://www.lasegunda.com{link}"
                            description = self.extract_summary(full_link)

                            # Fallback: si no hay descripción, crear una por defecto
                            if not description or len(description) < 100:
                                description = f"{title}\n\n[Haz clic en 'Leer más' para ver el artículo completo en La Segunda]"

                            self.news_items.append({
                                'diary': 'La Segunda',
                                'title': title,
                                'description': description,
                                'link': full_link,
                                'published': '',
                                'timestamp': datetime.now().isoformat()
                            })
                            count += 1
                except:
                    pass

            logger.info(f"La Segunda (resúmenes mejorados): {count} noticias")
        except Exception as e:
            logger.error(f"La Segunda: {e}")

    def _login_df(self):
        """Intenta hacer login en DF"""
        try:
            creds = self.credentials.get('df', {})
            if not creds:
                return False

            logger.info("Intentando autenticación en DF...")
            login_url = "https://www.df.cl/login"
            payload = {
                'email': creds.get('username', ''),
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

            # Intentar con Selenium si está disponible
            if SELENIUM_AVAILABLE:
                creds = self.credentials.get('df', {})
                if creds:
                    selenium_scraper = SeleniumScraper()
                    selenium_articles = selenium_scraper.scrape_df_with_selenium(
                        creds.get('username', ''),
                        creds.get('password', '')
                    )
                    if selenium_articles:
                        self.news_items.extend(selenium_articles)
                        logger.info(f"DF (Selenium): {len(selenium_articles)} noticias")
                        return

            # Fallback: extraer TODOS los links y filtrar por noticias
            self._login_df()
            response = self.session.get("https://www.df.cl", timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar todos los links que parecen noticias
            all_links = soup.find_all('a', href=True)
            seen_titles = set()
            count = 0

            for link_elem in all_links:
                try:
                    link = link_elem.get('href', '').strip()
                    title = link_elem.get_text().strip()

                    # Filtrar por URL que parecen noticias y títulos decentes
                    if (title and len(title) > 10 and len(title) < 200 and
                        ('/noticia/' in link or '/articulo/' in link or '/news/' in link or link.startswith('/')) and
                        title not in seen_titles):

                        seen_titles.add(title)
                        full_link = link if link.startswith('http') else f"https://www.df.cl{link}"
                        description = self.extract_summary(full_link)

                        if not description or len(description) < 100:
                            description = f"{title}\n\n[Haz clic en 'Leer más' para ver el artículo completo en DF]"

                        self.news_items.append({
                            'diary': 'DF',
                            'title': title,
                            'description': description,
                            'link': full_link,
                            'published': '',
                            'timestamp': datetime.now().isoformat()
                        })
                        count += 1
                        if count >= 15:
                            break
                except:
                    pass

            logger.info(f"DF: {count} noticias")
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
