from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import set_pub, get_pub


CRENEAUX = [
    ("matin", "🌅 Hadith du matin", "8h00"),
    ("midi",  "☀️ Verset de midi",  "13h00"),
    ("soir",  "🌇 Hadith du soir",  "18h00"),
    ("nuit",  "🌙 Invocation",      "21h00"),
]


def _keyboard(user_id: int):
    pub = get_pub(user_id)  # (matin, midi, soir, nuit)

    buttons = []
    for i, (key, label, heure) in enumerate(CRENEAUX):
        etat = "✅" if pub[i] == 1 else "❌"
        buttons.append([
            InlineKeyboardButton(
                f"{etat} {label} — {heure}",
                callback_data=f"notif_{key}"
            )
        ])
    buttons.append([InlineKeyboardButton("⬅️ Menu principal", callback_data="menu_back")])
    return InlineKeyboardMarkup(buttons)


def _texte():
    return (
        "🔔 *Notifications quotidiennes*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Clique sur un créneau pour l'activer ou le désactiver.\n\n"
        "🌅 *8h* — Hadith du matin\n"
        "☀️ *13h* — Verset du jour\n"
        "🌇 *18h* — Hadith du soir\n"
        "🌙 *21h* — Invocation\n\n"
        "💡 _Seuls les créneaux ✅ t'enverront un message._"
    )


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/notifications → menu des créneaux."""
    user_id = update.effective_user.id
    await update.message.reply_text(
        _texte(),
        reply_markup=_keyboard(user_id),
        parse_mode="Markdown"
    )


async def notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les créneaux."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data  # "notif_matin", "notif_midi", etc.

    key = data.replace("notif_", "")
    if key not in ("matin", "midi", "soir", "nuit"):
        return

    # Inverser l'état actuel
    pub = get_pub(user_id)
    idx = [c[0] for c in CRENEAUX].index(key)
    nouvel_etat = 0 if pub[idx] == 1 else 1
    set_pub(user_id, key, nouvel_etat)

    # Mettre à jour le menu
    try:
        await query.edit_message_text(
            _texte(),
            reply_markup=_keyboard(user_id),
            parse_mode="Markdown"
        )
    except Exception:
        pass