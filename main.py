#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import importlib.util
import logging
import os
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pollinibot")

# ---------------------------------------------------------------------------
# Verifica dipendenze
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = {
    "requests": "requests",
    "bs4": "beautifulsoup4",
    "playwright": "playwright",
    "dotenv": "python-dotenv",
    "telegram": "python-telegram-bot",
    "lxml": "lxml",
}

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_PATH = os.path.join(PROJECT_DIR, "requirements.txt")


def check_dependencies() -> None:
    missing = [
        pip_name
        for import_name, pip_name in REQUIRED_PACKAGES.items()
        if importlib.util.find_spec(import_name) is None
    ]
    if missing:
        print(f"📦 Librerie Python mancanti ({', '.join(missing)}), installazione in corso...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_PATH],
            check=True,
        )
        importlib.invalidate_caches()

    # Verifica/installa il browser Playwright (Chromium)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        install_dir = next(
            (
                line.split("Install location:", 1)[1].strip()
                for line in result.stdout.splitlines()
                if "Install location:" in line
            ),
            None,
        )
        if install_dir and not os.path.isdir(install_dir):
            print("📦 Browser Playwright (Chromium) non installato, installazione in corso...")
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
    except Exception as e:
        logger.warning("Impossibile verificare/installare Chromium per Playwright: %s", e)


# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------

def load_config() -> tuple[str, str]:
    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    errors = []
    if not token:
        errors.append("TELEGRAM_TOKEN non impostato nel file .env")
    if not chat_id:
        errors.append("TELEGRAM_CHAT_ID non impostato nel file .env")

    if errors:
        for err in errors:
            logger.error(err)
        print("\n❌ Configurazione mancante. Copia .env.example in .env e inserisci i valori.")
        sys.exit(1)

    return token, chat_id


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    check_dependencies()
    token, chat_id = load_config()

    logger.info("Avvio scraping ISPRA...")
    from scrapers import ispra
    ispra_data = ispra.scrape()

    if ispra_data:
        logger.info("ISPRA OK — periodo: %s", ispra_data.get("periodo"))
    else:
        logger.warning("ISPRA: nessun dato recuperato")

    logger.info("Avvio scraping 3bmeteo (Playwright)...")
    from scrapers import threebmeteo
    bmeteo_data = await threebmeteo.scrape()

    if bmeteo_data:
        logger.info("3bmeteo OK — %s", bmeteo_data)
    else:
        logger.warning("3bmeteo: nessun dato recuperato (il report verrà inviato senza questa fonte)")

    from telegram_sender import format_report, send
    report = format_report(ispra_data, bmeteo_data)

    logger.info("Invio report Telegram al chat %s...", chat_id)
    success = await send(token, chat_id, report)

    if success:
        logger.info("✅ Report inviato con successo")
    else:
        logger.error("❌ Invio fallito")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
