#!/usr/bin/env python3
"""
Exportador de PDFs diarios desde diarios con suscripción
Captura la edición digital completa de cada diario y guarda como PDF
"""
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class PDFExporter:
    def __init__(self, credentials_list):
        """
        Args:
            credentials_list: Lista de dicts con {diary, username, password}
        """
        self.credentials = {c['diary']: c for c in credentials_list}
        self.output_dir = Path('web/pdfs')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # URLs base de cada diario
        self.urls = {
            'mercurio': 'https://www.elmercurio.com',
            'tercera': 'https://www.latercera.com',
            'segunda': 'https://www.lasegunda.com',
            'df': 'https://www.df.cl'
        }

    def export_pdf(self, diary_key, diary_name):
        """Exporta la página principal de un diario a PDF"""
        try:
            if diary_key not in self.urls:
                logger.warning(f"Diario no configurado: {diary_key}")
                return False

            creds = self.credentials.get(diary_key)
            if not creds:
                logger.warning(f"Sin credenciales para {diary_name}")
                return False

            url = self.urls[diary_key]
            timestamp = datetime.now().strftime('%d%m%Y')
            output_file = self.output_dir / f"{diary_name}-{timestamp}.pdf"

            logger.info(f"Exportando PDF de {diary_name}...")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Navegar a la página
                page.goto(url, wait_until='networkidle', timeout=30000)

                # Intentar hacer login si es necesario (algunos diarios requieren)
                try:
                    self._try_login(page, diary_key, creds)
                except Exception as e:
                    logger.debug(f"Login fallido para {diary_name}: {e}")
                    # Continuar sin login, puede que la página sea accesible sin autenticación

                # Esperar a que cargue el contenido
                page.wait_for_load_state('networkidle')

                # Generar PDF de toda la página
                page.pdf(
                    path=str(output_file),
                    format='A4',
                    margin={'top': '0.5cm', 'bottom': '0.5cm', 'left': '0.5cm', 'right': '0.5cm'},
                    scale=0.8  # Reducir escala para que quepa mejor
                )

                browser.close()

                file_size_mb = output_file.stat().st_size / (1024 * 1024)
                logger.info(f"✅ PDF guardado: {output_file.name} ({file_size_mb:.1f} MB)")
                return True

        except PlaywrightTimeoutError:
            logger.error(f"Timeout exportando {diary_name}")
            return False
        except Exception as e:
            logger.error(f"Error exportando {diary_name}: {e}")
            return False

    def _try_login(self, page, diary_key, creds):
        """Intenta hacer login en un diario"""
        username = creds.get('username', '')
        password = creds.get('password', '')

        if not username or not password:
            return

        # Estrategia por diario
        if diary_key == 'mercurio':
            self._login_mercurio(page, username, password)
        elif diary_key == 'segunda':
            self._login_segunda(page, username, password)
        elif diary_key == 'df':
            self._login_df(page, username, password)
        elif diary_key == 'tercera':
            self._login_tercera(page, username, password)

    def _login_mercurio(self, page, username, password):
        """Login en El Mercurio"""
        try:
            # Buscar botón de login
            login_button = page.locator('button:has-text("Ingresar")')
            if login_button.count() > 0:
                login_button.first.click()
                page.wait_for_timeout(1000)

                # Rellenar credenciales
                page.fill('input[name="email"]', username)
                page.fill('input[name="password"]', password)
                page.click('button[type="submit"]')
                page.wait_for_load_state('networkidle')
        except Exception as e:
            logger.debug(f"Login Mercurio fallido: {e}")

    def _login_segunda(self, page, username, password):
        """Login en La Segunda"""
        try:
            # Buscar campo de login
            login_input = page.locator('input[placeholder*="correo"]')
            if login_input.count() > 0:
                login_input.first.fill(username)
                page.fill('input[type="password"]', password)
                page.click('button:has-text("Ingresar")')
                page.wait_for_load_state('networkidle')
        except Exception as e:
            logger.debug(f"Login La Segunda fallido: {e}")

    def _login_df(self, page, username, password):
        """Login en DF"""
        try:
            page.fill('input[name="email"]', username)
            page.fill('input[name="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_load_state('networkidle')
        except Exception as e:
            logger.debug(f"Login DF fallido: {e}")

    def _login_tercera(self, page, username, password):
        """Login en La Tercera"""
        try:
            page.fill('input[type="email"]', username)
            page.fill('input[type="password"]', password)
            page.click('button:has-text("Entrar")')
            page.wait_for_load_state('networkidle')
        except Exception as e:
            logger.debug(f"Login La Tercera fallido: {e}")

    def export_all(self):
        """Exporta PDFs de todos los diarios disponibles"""
        results = {
            'mercurio': self.export_pdf('mercurio', 'ElMercurio'),
            'tercera': self.export_pdf('tercera', 'LaTerecra'),
            'segunda': self.export_pdf('segunda', 'LaSegunda'),
            'df': self.export_pdf('df', 'DF'),
        }

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(f"PDFs exportados: {success_count}/{total_count}")
        return results
