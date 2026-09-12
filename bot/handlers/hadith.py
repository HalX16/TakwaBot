import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

HADITHS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "hadiths.json"
)

with open(HADITHS_PATH, "r", encoding="utf-8") as f:
    HADITHS = json.load(f)


def format_hadith(h: dict) -> str:
    msg = f"🕋 *Hadith du jour*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"_{h['texte']}_\n\n"
    if h.get("source"):
        msg += f"📚 Source : {h['source']}"
    return msg


def _keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Autre hadith", callback_data="hadith_next")]
    ])


async def hadith_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche un hadith aléatoire."""
    h = random.choice(HADITHS)
    await update.message.reply_text(
        format_hadith(h),
        reply_markup=_keyboard(),
        parse_mode="Markdown"
    )


async def hadith_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bouton 'Autre hadith' → affiche un nouveau hadith."""
    query = update.callback_query
    await query.answer("🔄 Nouveau hadith...")

    h = random.choice(HADITHS)
    try:
        await query.edit_message_text(
            format_hadith(h),
            reply_markup=_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"⚠️ Erreur edit hadith : {e}")