from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

URL = "https://www.3bmeteo.com/meteo/cagliari/pollini"

# Mapping testo trovato sulla pagina → chiave canonica
POLLEN_KEYWORDS: dict[str, str] = {
    "composit": "compositae",
    "parietari": "urticaceae",
    "urticac": "urticaceae",
    "urticee": "urticaceae",
    "cipressac": "cupressaceae",
    "taxac": "cupressaceae",
    "cupressac": "cupressaceae",
}

# Etichette di categoria così come riportate da 3bmeteo, in ordine di
# verifica: le forme "molto ..." vanno controllate prima delle forme brevi
# (es. "molto basso" contiene "basso").
CATEGORY_LABELS: list[tuple[str, str]] = [
    ("molto basso", "MOLTO BASSO"),
    ("molto bassa", "MOLTO BASSO"),
    ("molto alto", "MOLTO ALTO"),
    ("molto alta", "MOLTO ALTO"),
    ("assente", "ASSENTE"),
    ("basso", "BASSO"),
    ("bassa", "BASSO"),
    ("medio", "MEDIO"),
    ("media", "MEDIO"),
    ("alto", "ALTO"),
    ("alta", "ALTO"),
]


def _extract_category_label(text: str) -> str | None:
    """Estrae l'etichetta di categoria originale di 3bmeteo (es. "MEDIO"), senza convertirla in un valore numerico."""
    text_lower = text.strip().lower()
    for key, label in CATEGORY_LABELS:
        if key in text_lower:
            return label
    return None


def _match_pollen_key(text: str) -> str | None:
    text_lower = text.lower()
    for keyword, canonical in POLLEN_KEYWORDS.items():
        if keyword in text_lower:
            return canonical
    return None


def _extract_update_time(soup) -> str | None:
    """Estrae l'orario di aggiornamento riportato dalla pagina (es. "14 giugno alle ore 12:12")."""
    elem = soup.find(string=re.compile(r"Aggiornamento:", re.I))
    if elem is None:
        return None
    match = re.search(r"Aggiornamento:\s*(.+)", elem, re.I)
    return match.group(1).strip() if match else None


async def _scrape_async() -> dict | None:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright non installato. Esegui: pip install playwright && playwright install chromium")
        return None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="it-IT",
        )
        page = await context.new_page()

        try:
            await page.goto(URL, timeout=30000, wait_until="domcontentloaded")
            # Attende un po' per il rendering JS
            await page.wait_for_timeout(3000)

            content = await page.content()
            await browser.close()
        except Exception as e:
            logger.error("3bmeteo Playwright error durante navigazione: %s", e)
            await browser.close()
            return None

    return _parse_html(content)


def _parse_html(html: str) -> dict | None:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("beautifulsoup4 non installato")
        return None

    soup = BeautifulSoup(html, "lxml")
    update_time = _extract_update_time(soup)
    result: dict = {}
    source = None

    # Strategia 1: cerca righe di tabella con nome polline + categoria
    for row in soup.find_all("tr"):
        cells = row.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        pollen_key = _match_pollen_key(cells[0].get_text())
        if pollen_key:
            value_text = cells[-1].get_text()
            label = _extract_category_label(value_text)
            if label is not None:
                result[pollen_key] = label
    if result:
        source = "tabella"

    # Strategia 2: cerca elementi con classe contenente "pollin" o simili
    if not result:
        for elem in soup.find_all(class_=re.compile(r"pollin|pollen", re.I)):
            text = elem.get_text(" ", strip=True)
            pollen_key = _match_pollen_key(text)
            if pollen_key:
                label = _extract_category_label(text)
                if label is not None and pollen_key not in result:
                    result[pollen_key] = label
        if result:
            source = "classi"

    # Strategia 3: testo libero — cerca paragrafi/div che menzionano il polline
    if not result:
        for elem in soup.find_all(["p", "div", "li", "span"]):
            text = elem.get_text(" ", strip=True)
            if len(text) > 200:
                continue
            pollen_key = _match_pollen_key(text)
            if pollen_key and pollen_key not in result:
                label = _extract_category_label(text)
                if label is not None:
                    result[pollen_key] = label
        if result:
            source = "testo libero"

    if not result:
        logger.warning("3bmeteo: nessun dato pollinico trovato nella pagina")
        return None

    if update_time:
        result["aggiornamento"] = update_time

    logger.info("3bmeteo data (da %s): %s", source, result)
    return result


async def scrape() -> dict | None:
    """
    Entry point asincrono. Restituisce un dizionario con le etichette di
    categoria originali di 3bmeteo, es.:
      {
        "compositae": "ASSENTE",
        "urticaceae": "MEDIO",
        "cupressaceae": "ASSENTE",
      }
    Restituisce None in caso di errore.
    """
    try:
        return await _scrape_async()
    except Exception as e:
        logger.error("3bmeteo scrape error: %s", e)
        return None
