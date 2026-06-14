from __future__ import annotations

THRESHOLDS: dict[str, list[tuple[float, str, str]]] = {
    "compositae": [
        (30.0, "🔴", "ALTO"),
        (10.0, "🟡", "MEDIO"),
        (3.0,  "🟢", "BASSO"),
        (0.0,  "⚫", "ASSENTE"),
    ],
    "urticaceae": [
        (80.0, "🔴", "ALTO"),
        (20.0, "🟡", "MEDIO"),
        (3.0,  "🟢", "BASSO"),
        (0.0,  "⚫", "ASSENTE"),
    ],
    "cupressaceae": [
        (50.0, "🔴", "ALTO"),
        (15.0, "🟡", "MEDIO"),
        (3.0,  "🟢", "BASSO"),
        (0.0,  "⚫", "ASSENTE"),
    ],
}

# Alias per nomi alternativi trovati nelle pagine
ALIASES: dict[str, str] = {
    "taxaceae": "cupressaceae",
    "cupressaceae/taxaceae": "cupressaceae",
    "parietaria": "urticaceae",
    "composite": "compositae",
    "cipressacee": "cupressaceae",
    "taxacee": "cupressaceae",
    "parietarie": "urticaceae",
    "urticacee": "urticaceae",
}

ITALIAN_NAMES: dict[str, str] = {
    "compositae": "Composite",
    "urticaceae": "Parietaria/Urticacee",
    "cupressaceae": "Cipressacee/Taxacee",
}

# Emoji per le etichette di categoria testuali (es. quelle riportate da 3bmeteo)
LABEL_EMOJI: dict[str, str] = {
    "assente": "⚫",
    "molto basso": "🟢",
    "basso": "🟢",
    "medio": "🟡",
    "alto": "🔴",
    "molto alto": "🔴",
}


def normalize_key(pollen_type: str) -> str:
    key = pollen_type.strip().lower()
    return ALIASES.get(key, key)


def categorize(pollen_type: str, value: float) -> tuple[str, str]:
    """Restituisce (emoji, label) per il valore p/m³ dato il tipo di polline."""
    key = normalize_key(pollen_type)
    thresholds = THRESHOLDS.get(key, THRESHOLDS["compositae"])
    for min_val, emoji, label in thresholds:
        if value >= min_val:
            return emoji, label
    return "⚫", "ASSENTE"


def italian_name(pollen_type: str) -> str:
    key = normalize_key(pollen_type)
    return ITALIAN_NAMES.get(key, pollen_type.title())


def emoji_for_label(label: str) -> str:
    """Restituisce l'emoji corrispondente a un'etichetta di categoria testuale (es. "MEDIO")."""
    return LABEL_EMOJI.get(label.strip().lower(), "❓")
