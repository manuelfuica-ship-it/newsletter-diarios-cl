#!/usr/bin/env python3
"""
Scraper con Playwright para diarios con JavaScript rendering
"""
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class PlaywrightScraper:
    def __init__(self):
        self.browser = None
        self.news_items = []

    def scrape_article_content(self, url):
        """Extrae CONTENIDO COMPLETO de un artículo usando Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until='networkidle', timeout=15000)

                soup = BeautifulSoup(page.content(), 'html.parser')
                browser.close()

                # Buscar contenedor de artículo
                article = soup.find('article') or soup.find('main') or soup.find(['div', 'section'], class_=lambda x: x and ('content' in str(x).lower() or 'article' in str(x).lower()))

                if not article:
                    article = soup.body

                if article:
                    paragraphs = article.find_all('p')
                    content_lines = []

                    for p in paragraphs:
                        text = p.get_text().strip()
                        if text and len(text) > 10:
                            content_lines.append(text)

                    for heading in article.find_all(['h2', 'h3']):
                        text = heading.get_text().strip()
                        if text:
                            content_lines.append(f"\n{text}\n")

                    content = '\n\n'.join(content_lines)
                    return content if content and len(content) > 200 else None

            return None
        except Exception as e:
            logger.debug(f"Error extrayendo contenido de {url}: {e}")
            return None

    def scrape_mercurio(self, username, password):
        """Scraping de El Mercurio con Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Navegar a la página
                page.goto("https://www.elmercurio.com", wait_until='networkidle', timeout=20000)

                # Buscar artículos
                soup = BeautifulSoup(page.content(), 'html.parser')
                articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in str(x).lower(), limit=15)

                news_items = []
                for article in articles:
                    try:
                        title_elem = article.find(['h2', 'h3', 'a'])
                        link_elem = article.find('a', href=True)

                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            link = link_elem.get('href', '')

                            if len(title) > 5 and link:
                                full_link = link if link.startswith('http') else f"https://www.elmercurio.com{link}"
                                content = self.scrape_article_content(full_link)

                                news_items.append({
                                    'diary': 'El Mercurio',
                                    'title': title,
                                    'description': content or title,
                                    'link': full_link,
                                    'published': '',
                                    'timestamp': datetime.now().isoformat()
                                })
                    except:
                        pass

                browser.close()
                logger.info(f"El Mercurio (Playwright): {len(news_items)} noticias")
                return news_items

        except Exception as e:
            logger.error(f"Error en scraping Playwright El Mercurio: {e}")
            return []

    def scrape_segunda(self, username, password):
        """Scraping de La Segunda con Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto("https://www.lasegunda.com", wait_until='networkidle', timeout=20000)

                soup = BeautifulSoup(page.content(), 'html.parser')
                articles = soup.find_all('article', limit=15)

                news_items = []
                for article in articles:
                    try:
                        title_elem = article.find(['h2', 'h3', 'a'])
                        link_elem = article.find('a', href=True)

                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            link = link_elem.get('href', '')

                            if len(title) > 5 and link:
                                full_link = link if link.startswith('http') else f"https://www.lasegunda.com{link}"
                                content = self.scrape_article_content(full_link)

                                news_items.append({
                                    'diary': 'La Segunda',
                                    'title': title,
                                    'description': content or title,
                                    'link': full_link,
                                    'published': '',
                                    'timestamp': datetime.now().isoformat()
                                })
                    except:
                        pass

                browser.close()
                logger.info(f"La Segunda (Playwright): {len(news_items)} noticias")
                return news_items

        except Exception as e:
            logger.error(f"Error en scraping Playwright La Segunda: {e}")
            return []

    def scrape_df(self, username, password):
        """Scraping de DF con Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto("https://www.df.cl", wait_until='networkidle', timeout=20000)

                soup = BeautifulSoup(page.content(), 'html.parser')
                articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in str(x).lower(), limit=15)

                news_items = []
                for article in articles:
                    try:
                        title_elem = article.find(['h2', 'h3', 'a'])
                        link_elem = article.find('a', href=True)

                        if title_elem and link_elem:
                            title = title_elem.get_text().strip()
                            link = link_elem.get('href', '')

                            if len(title) > 5 and link:
                                full_link = link if link.startswith('http') else f"https://www.df.cl{link}"
                                content = self.scrape_article_content(full_link)

                                news_items.append({
                                    'diary': 'DF',
                                    'title': title,
                                    'description': content or title,
                                    'link': full_link,
                                    'published': '',
                                    'timestamp': datetime.now().isoformat()
                                })
                    except:
                        pass

                browser.close()
                logger.info(f"DF (Playwright): {len(news_items)} noticias")
                return news_items

        except Exception as e:
            logger.error(f"Error en scraping Playwright DF: {e}")
            return []
