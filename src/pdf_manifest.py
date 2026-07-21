#!/usr/bin/env python3
"""
Genera un manifest JSON de los PDFs disponibles en web/pdfs/
para que la página web pueda listarlos
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_manifest(pdfs_dir='web/pdfs', output_file='web/data/pdfs-manifest.json'):
    """
    Genera manifest.json con información de todos los PDFs
    """
    try:
        pdfs_path = Path(pdfs_dir)
        output_path = Path(output_file)

        # Crear directorio si no existe
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Buscar todos los PDFs
        manifest = {
            'ElMercurio': [],
            'LaTerecra': [],
            'LaSegunda': [],
            'DF': [],
            'lastUpdated': datetime.now().isoformat()
        }

        if pdfs_path.exists():
            for pdf_file in sorted(pdfs_path.glob('*.pdf'), reverse=True):
                # Parsear nombre: DIARIO-DDMMYYYY.pdf
                name = pdf_file.stem  # sin .pdf
                parts = name.rsplit('-', 1)

                if len(parts) == 2:
                    diario_key = parts[0]
                    if diario_key in manifest:
                        manifest[diario_key].append({
                            'filename': pdf_file.name,
                            'size': pdf_file.stat().st_size,
                            'date': parts[1]  # DDMMYYYY
                        })

        # Guardar manifest
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"Manifest generado: {output_file}")

        # Mostrar resumen
        total_pdfs = sum(len(v) for k, v in manifest.items() if k != 'lastUpdated')
        logger.info(f"Total PDFs indexados: {total_pdfs}")

        return True

    except Exception as e:
        logger.error(f"Error generando manifest: {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_manifest()
