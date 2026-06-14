from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

POLLEN_ORDER = ["compositae", "urticaceae", "cupressaceae"]


def _escape_md(text: str) -> str:
    """Escapa caratteri speciali per MarkdownV2 di Telegram."""
    special = r"\_*[]()~`>#+-=|{}.!"
    for ch in special:
        text = text.replace(ch, f"\\{ch}")
    return text


def _format_ispra_block(data: dict | None) -> str:
    from pollen import categorize, italian_name

    if data is None:
        return "*Fonte: ISPRA POLLnet*\n_dati non disponibili_\n"

    lines = ["*Fonte: ISPRA POLLnet*"]
    periodo = data.get("periodo")
    if periodo:
        lines.append(f"📅 Settimana: {_escape_md(periodo)}")
    for key in POLLEN_ORDER:
        if key not in data:
            continue
        value = data[key]
        emoji, label = categorize(key, value)
        name = _escape_md(italian_name(key))
        label_esc = _escape_md(label)
        val_str = _escape_md(f"{value:.1f} p/m³")
        lines.append(f"{emoji} {name}: {label_esc} \\({val_str}\\)")

    return "\n".join(lines)


def _format_bmeteo_block(data: dict | None) -> str:
    from pollen import emoji_for_label, italian_name

    if data is None:
        return "*Fonte: 3bmeteo*\n_dati non disponibili_\n"

    lines = ["*Fonte: 3bmeteo*"]
    aggiornamento = data.get("aggiornamento")
    if aggiornamento:
        lines.append(f"📅 Aggiornamento: {_escape_md(aggiornamento)}")
    for key in POLLEN_ORDER:
        if key not in data:
            continue
        label = data[key]
        emoji = emoji_for_label(label)
        name = _escape_md(italian_name(key))
        label_esc = _escape_md(label)
        lines.append(f"{emoji} {name}: {label_esc}")

    return "\n".join(lines)


def format_report(ispra_data: dict | None, bmeteo_data: dict | None) -> str:
    header = "🌿 *Report Pollini Cagliari*"

    ispra_block = _format_ispra_block(ispra_data)
    bmeteo_block = _format_bmeteo_block(bmeteo_data)

    legend = "ℹ️ Legenda: 🟢 Basso \\| 🟡 Medio \\| 🔴 Alto \\| ⚫ Assente"

    return "\n\n".join([header, ispra_block, bmeteo_block, legend])


async def send(token: str, chat_id: str, text: str) -> bool:
    """Invia il messaggio al gruppo Telegram. Restituisce True se successo."""
    try:
        from telegram import Bot
        from telegram.constants import ParseMode

        bot = Bot(token=token)
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.info("Messaggio inviato correttamente a %s", chat_id)
        return True
    except Exception as e:
        logger.error("Errore invio Telegram: %s", e)
        return False
