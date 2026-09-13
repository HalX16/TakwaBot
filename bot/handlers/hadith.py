import json
import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import get_langue


HADITHS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "hadiths.json"
)

with open(HADITHS_PATH, "r", encoding="utf-8") as f:
    HADITHS = json.load(f)


# ============================================================
#   API fawazahmed0 — hadiths authentiques en AR / EN
# ============================================================

API_BASE = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions"

# Éditions disponibles : ara-bukhari, ara-muslim, eng-bukhari, eng-muslim
EDITIONS = {
    "ar": ["ara-bukhari", "ara-muslim"],
    "en": ["eng-bukhari", "eng-muslim"],
}

# Nombre total de hadiths par édition (approximatif, on tirera au hasard)
TOTAL_HADITHS = {
    "ara-bukhari": 7563,
    "ara-muslim": 3032,
    "eng-bukhari": 7563,
    "eng-muslim": 3032,
}


def fetch_hadith_api(langue: str):
    """Récupère un hadith aléatoire depuis l'API selon la langue."""
    editions = EDITIONS.get(langue)
    if not editions:
        return None

    edition = random.choice(editions)
    total = TOTAL_HADITHS.get(edition, 100)

    # Essaie jusqu'à 5 fois (certains numéros peuvent ne pas exister)
    for _ in range(5):
        numero = random.randint(1, total)
        url = f"{API_BASE}/{edition}/{numero}.min.json"
        try:
            r = requests.get(url, timeout=8)
            if r.status_code != 200:
                continue
            data = r.json()
            hadiths = data.get("hadiths", [])
            if not hadiths:
                continue
            h = hadiths[0]
            return {
                "texte": h.get("text", ""),
                "numero": h.get("hadithnumber"),
                "source": data.get("metadata", {}).get("name", edition),
                "livre": list(data.get("metadata", {}).get("section", {}).values())[0]
                    if data.get("metadata", {}).get("section") else "",
                "edition": edition,
            }
        except Exception as e:
            print(f"⚠️ Erreur API : {e}")
            continue
    return None


# ============================================================
#   Formatage
# ============================================================

def format_hadith(h: dict) -> str:
    msg = "🕋 *Hadith du jour*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"{h['texte']}\n\n"

    source = h.get("source", "")
    numero = h.get("numero")
    livre = h.get("livre", "")

    if source and numero:
        msg += f"📚 {source} — n°{numero}\n"
    elif source:
        msg += f"📚 {source}\n"

    if livre:
        msg += f"📖 _{livre}_"

    return msg


def get_hadith(langue: str):
    """Retourne un hadith selon la langue (local FR, API AR/EN)."""
    if langue == "fr":
        return random.choice(HADITHS)

    # AR ou EN → API
    h = fetch_hadith_api(langue)
    if h:
        return h

    # Fallback : français local si l'API échoue
    print(f"⚠️ API indisponible pour {langue}, fallback FR")
    return random.choice(HADITHS)


def _keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Autre hadith", callback_data="hadith_next"),
            InlineKeyboardButton("💝 Soutenir", callback_data="don_menu"),
        ],
        [
            InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back"),
        ]
    ])


# ============================================================
#   /hadith
# ============================================================

async def _reply(update: Update, text: str, **kwargs):
    """Répond soit à un message, soit à un callback."""
    if update.callback_query:
        await update.callback_query.message.reply_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)


async def hadith_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    langue = get_langue(user_id)

    h = get_hadith(langue)
    await _reply(update,
        format_hadith(h),
        reply_markup=_keyboard(),
        parse_mode="Markdown"
    )


async def hadith_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🔄 Nouveau hadith...")

    user_id = query.from_user.id
    langue = get_langue(user_id)

    h = get_hadith(langue)
    try:
        await query.edit_message_text(
            format_hadith(h),
            reply_markup=_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"⚠️ Erreur edit hadith : {e}")