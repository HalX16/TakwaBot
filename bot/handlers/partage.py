from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# ============================================================
#   Configuration du partage
# ============================================================

# ⚠️ Remplace ce username par le vrai username de ton bot (sans @)
BOT_USERNAME = "TkwaHBot"

# Texte qui accompagne le lien
SHARE_TEXT = "🕌 Découvre TakwaBot, ton compagnon spirituel sur Telegram : Coran, hadiths, horaires de prière, Qibla et plus encore !"


def share_url():
    """Construit l'URL de partage Telegram."""
    from urllib.parse import quote
    texte_encode = quote(SHARE_TEXT)
    bot_url = f"https://t.me/{BOT_USERNAME}"
    return f"https://t.me/share/url?url={bot_url}&text={texte_encode}"


def bouton_partage():
    """Retourne un bouton inline 'Partager'."""
    return InlineKeyboardButton("📤 Partager TakwaHBot", url=share_url())


def keyboard_partage():
    """Retourne un clavier avec le bouton de partage seul."""
    return InlineKeyboardMarkup([[bouton_partage()]])


# ============================================================
#   Commande /partager
# ============================================================

async def partager_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/partager → propose de partager le bot."""
    await update.message.reply_text(
        "📤 *Partage TakwaBot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Tu aimes TakwaBot ? Partage-le autour de toi !\n\n"
        "Chaque personne qui rejoint la communauté nous aide "
        "à améliorer le bot in shaa Allah.\n\n"
        "🤲 JazakAllah khair pour ton soutien !",
        reply_markup=keyboard_partage(),
        parse_mode="Markdown"
    )