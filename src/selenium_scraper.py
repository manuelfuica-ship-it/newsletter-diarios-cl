#!/usr/bin/env python3
"""
Scraper con Selenium para diarios con JavaScript rendering y paywall
"""
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class SeleniumScraper:
    def __init__(self):
        self.driver = None
        self.news_items = []

    def init_driver(self, headless=True):
        """Inicializar ChromeDriver"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("ChromeDriver inicializado")
            return True
        except Exception as e:
            logger.error(f"Error inicializando ChromeDriver: {e}")
            return False

    def login_segunda(self, username, password):
        """Hacer login en La Segunda"""
        try:
            logger.info("Intentando login en La Segunda...")
            self.driver.get("https://www.lasegunda.com")

            # Esperar a que cargue la página
            wait = WebDriverWait(self.driver, 10)

            # Intentar encontrar botón de login
            login_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'login')] | //button[contains(text(), 'Ingresar')]")
            if login_buttons:
                login_buttons[0].click()

            # Rellenar formulario de login
            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            self.driver.find_element(By.NAME, "email").send_keys(username)
            self.driver.find_element(By.NAME, "password").send_keys(password)

            # Hacer click en login
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar')] | //input[@value='Ingresar']")
            login_btn.click()

            # Esperar a que inicie sesión
            wait.until(EC.url_changes(self.driver.current_url))
            logger.info("Login en La Segunda exitoso")
            return True
        except Exception as e:
            logger.debug(f"Login La Segunda fallido: {e}")
            return False

    def scrape_article_content(self, url):
        """Extraer contenido de un artículo usando Selenium"""
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)

            # Esperar a que cargue el contenido principal
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "article")))

            # Extraer contenido
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Buscar artículo
            article = soup.find('article') or soup.find('main')
            if article:
                # Extraer texto del artículo
                paragraphs = article.find_all('p')
                content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                return content[:2000]  # Primeros 2000 caracteres

            return ""
        except Exception as e:
            logger.debug(f"Error extrayendo contenido del artículo: {e}")
            return ""

    def scrape_segunda_with_selenium(self, username, password):
        """Scraping de La Segunda usando Selenium"""
        try:
            if not self.init_driver(headless=True):
                logger.error("No se pudo inicializar ChromeDriver")
                return []

            # Hacer login
            if not self.login_segunda(username, password):
                logger.warning("No se pudo hacer login en La Segunda, usando fallback")
                return []

            self.driver.get("https://www.lasegunda.com")

            # Esperar a que carguen las noticias
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            articles = soup.find_all('article', limit=20)

            news_items = []
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a', href=True)

                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        link = link_elem.get('href', '')

                        if len(title) > 5 and link:
                            # Extraer contenido del artículo
                            full_link = link if link.startswith('http') else f"https://www.lasegunda.com{link}"
                            content = self.scrape_article_content(full_link)

                            news_items.append({
                                'diary': 'La Segunda',
                                'title': title,
                                'description': content,
                                'link': full_link,
                                'published': '',
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass

            logger.info(f"La Segunda (Selenium): {len(news_items)} noticias")
            return news_items

        except Exception as e:
            logger.error(f"Error en scraping Selenium: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

    def login_mercurio(self, username, password):
        """Hacer login en El Mercurio"""
        try:
            logger.info("Intentando login en El Mercurio...")
            self.driver.get("https://www.elmercurio.com")
            wait = WebDriverWait(self.driver, 10)

            # Buscar formulario de login
            login_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'login')] | //button[contains(text(), 'Ingresar')]")
            if login_buttons:
                login_buttons[0].click()

            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            self.driver.find_element(By.NAME, "email").send_keys(username)
            self.driver.find_element(By.NAME, "password").send_keys(password)

            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar')]")
            login_btn.click()

            wait.until(EC.url_changes(self.driver.current_url))
            logger.info("Login en El Mercurio exitoso")
            return True
        except Exception as e:
            logger.debug(f"Login El Mercurio fallido: {e}")
            return False

    def scrape_mercurio_with_selenium(self, username, password):
        """Scraping de El Mercurio usando Selenium"""
        try:
            if not self.init_driver(headless=True):
                logger.error("No se pudo inicializar ChromeDriver")
                return []

            if not self.login_mercurio(username, password):
                logger.warning("No se pudo hacer login en El Mercurio")
                return []

            self.driver.get("https://www.elmercurio.com")
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            articles = soup.find_all('article', limit=20)

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
                                'description': content,
                                'link': full_link,
                                'published': '',
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass

            logger.info(f"El Mercurio (Selenium): {len(news_items)} noticias")
            return news_items
        except Exception as e:
            logger.error(f"Error en scraping El Mercurio: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

    def login_df(self, username, password):
        """Hacer login en DF"""
        try:
            logger.info("Intentando login en DF...")
            self.driver.get("https://www.df.cl")
            wait = WebDriverWait(self.driver, 10)

            login_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'login')] | //button[contains(text(), 'Ingresar')]")
            if login_buttons:
                login_buttons[0].click()

            wait.until(EC.presence_of_element_located((By.NAME, "email")))
            self.driver.find_element(By.NAME, "email").send_keys(username)
            self.driver.find_element(By.NAME, "password").send_keys(password)

            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ingresar')]")
            login_btn.click()

            wait.until(EC.url_changes(self.driver.current_url))
            logger.info("Login en DF exitoso")
            return True
        except Exception as e:
            logger.debug(f"Login DF fallido: {e}")
            return False

    def scrape_df_with_selenium(self, username, password):
        """Scraping de DF usando Selenium"""
        try:
            if not self.init_driver(headless=True):
                logger.error("No se pudo inicializar ChromeDriver")
                return []

            if not self.login_df(username, password):
                logger.warning("No se pudo hacer login en DF")
                return []

            self.driver.get("https://www.df.cl")
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "article")))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            articles = soup.find_all('article', limit=20)

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
                                'description': content,
                                'link': full_link,
                                'published': '',
                                'timestamp': datetime.now().isoformat()
                            })
                except:
                    pass

            logger.info(f"DF (Selenium): {len(news_items)} noticias")
            return news_items
        except Exception as e:
            logger.error(f"Error en scraping DF: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()

    def close(self):
        """Cerrar el navegador"""
        if self.driver:
            self.driver.quit()
