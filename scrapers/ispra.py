from __future__ import annotations

import logging
import re

import requests
from bs4 import BeautifulSoup

from pollen import normalize_key

logger = logging.getLogger(__name__)

URL = "https://pollnet.isprambiente.it/menumappe/mappa-bollettini/bollettino-settimanale-dei-pollini/?stat_id=CA7"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Chiavi canoniche dei pollini di interesse (vedi pollen.py)
TARGET_POLLENS = {"compositae", "urticaceae", "cupressaceae"}


def _extract_period(soup: BeautifulSoup) -> str:
    """Estrae il periodo del bollettino dal testo della pagina (es. "dal 01/06/2026 al 07/06/2026")."""
    text = soup.get_text(" ", strip=True)
    match = re.search(
        r"situazione.*?dal\s+(\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})",
        text, re.IGNORECASE,
    )
    if not match:
        match = re.search(
            r"dal\s+(\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})",
            text, re.IGNORECASE,
        )
    if match:
        return f"{match.group(1)} – {match.group(2)}"
    return "periodo non disponibile"


def scrape() -> dict | None:
    """
    Restituisce un dizionario con:
      {
        "periodo": "01/06/2026 – 07/06/2026",
        "compositae": 0.9,
        "urticaceae": 12.5,
        "cupressaceae": 4.69,
      }
    Restituisce None in caso di errore.
    """
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("ISPRA fetch error: %s", e)
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    periodo = _extract_period(soup)

    # Cerca la tabella settimanale: ha una colonna "Media Settimanale" nell'intestazione
    # e i nomi dei pollini nella prima cella di ogni riga dati.
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if not rows:
            continue

        header_cells = [c.get_text(strip=True).lower() for c in rows[0].find_all(["th", "td"])]
        if "media settimanale" not in header_cells:
            continue

        media_idx = header_cells.index("media settimanale")
        result: dict = {"periodo": periodo}

        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            if len(cells) <= media_idx:
                continue

            canonical = normalize_key(cells[0].get_text(strip=True))
            if canonical not in TARGET_POLLENS:
                continue

            raw = cells[media_idx].get_text(strip=True).replace(",", ".")
            # Rimuove tutto ciò che non è numerico o punto decimale
            numeric = re.sub(r"[^\d.]", "", raw)
            try:
                result[canonical] = float(numeric)
            except ValueError:
                result[canonical] = 0.0

        if any(k in result for k in TARGET_POLLENS):
            logger.info("ISPRA data: %s", result)
            return result

    logger.error("ISPRA: nessuna tabella pollinica trovata")
    return None
