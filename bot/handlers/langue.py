from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import set_langue, get_langue


LANGUES = {
    "fr": "Français 🇫🇷",
    "en": "English 🇬🇧",
    "ar": "العربية 🇸🇦",
}


def _keyboard_langues():
    """Construit le clavier avec les 3 langues."""
    buttons = [
        [InlineKeyboardButton(LANGUES["fr"], callback_data="lang_fr")],
        [InlineKeyboardButton(LANGUES["en"], callback_data="lang_en")],
        [InlineKeyboardButton(LANGUES["ar"], callback_data="lang_ar")],
    ]
    return InlineKeyboardMarkup(buttons)


async def langue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/langue → affiche les boutons. /langue fr|en|ar → change directement."""
    user_id = update.effective_user.id

    # Si un argument est fourni, on change directement
    if context.args:
        code = context.args[0].lower()
        if code not in LANGUES:
            await update.message.reply_text(
                "⚠️ Langue invalide. Choisis : `fr`, `en` ou `ar`.",
                parse_mode="Markdown"
            )
            return
        set_langue(user_id, code)
        await update.message.reply_text(
            f"✅ Langue changée : *{LANGUES[code]}*\n\n"
            f"Tape `/sourate 1` pour tester.",
            parse_mode="Markdown"
        )
        return

    # Sinon : affiche les boutons
    actuelle = get_langue(user_id)
    await update.message.reply_text(
        f"🌍 *Choisis ta langue*\n\n"
        f"Langue actuelle : *{LANGUES.get(actuelle, actuelle)}*\n\n"
        f"ℹ️ La langue change la traduction du Coran. "
        f"Le texte arabe reste toujours affiché.",
        reply_markup=_keyboard_langues(),
        parse_mode="Markdown"
    )


async def langue_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère le clic sur un bouton de langue."""
    query = update.callback_query
    await query.answer()

    data = query.data  # "lang_fr", "lang_en" ou "lang_ar"
    code = data.split("_", 1)[1]

    if code not in LANGUES:
        await query.edit_message_text("⚠️ Langue invalide.")
        return

    user_id = query.from_user.id
    set_langue(user_id, code)

    await query.edit_message_text(
        f"✅ Langue changée : *{LANGUES[code]}*\n\n"
        f"Tape `/sourate 1` pour tester.",
        parse_mode="Markdown"
    )