from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# ============================================================
#   Menu principal
# ============================================================

def _menu_principal():
    """Construit le menu principal avec boutons."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Coran", callback_data="menu_quran"),
            InlineKeyboardButton("🕋 Hadith", callback_data="menu_hadith"),
        ],
        [
            InlineKeyboardButton("📿 Prière", callback_data="menu_priere"),
            InlineKeyboardButton("🧭 Qibla", callback_data="menu_qibla"),
        ],
        [
            InlineKeyboardButton("🌙 Hijri", callback_data="menu_hijri"),
            InlineKeyboardButton("📚 Bibliothèque", callback_data="menu_biblio"),
        ],
        [
            InlineKeyboardButton("📍 Ma ville", callback_data="menu_ville"),
            InlineKeyboardButton("🌍 Langue", callback_data="menu_langue"),
        ],
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="menu_notif"),
            InlineKeyboardButton("💝 Soutenir", callback_data="don_menu"),
        ],
        [
            InlineKeyboardButton("📋 Toutes les commandes", callback_data="menu_help"),
        ],
    ])


def _menu_texte():
    return (
        "🕌 *TakwaBot — Menu principal*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choisis une option ci-dessous 👇\n\n"
        "💡 _Tu peux aussi utiliser les commandes directes "
        "(ex: `/hadith`, `/priere`)._"
    )


# ============================================================
#   Menu secondaires (sous-menus)
# ============================================================

def _menu_quran():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎲 Sourate aléatoire", callback_data="menu_quran_random"),
            InlineKeyboardButton("📚 Les 114 sourates", callback_data="menu_quran_liste"),
        ],
        [
            InlineKeyboardButton("🔍 Rechercher un mot", callback_data="menu_quran_search"),
            InlineKeyboardButton("📖 Verset précis", callback_data="menu_quran_verset"),
        ],
        [
            InlineKeyboardButton("⬅️ Menu principal", callback_data="menu_back"),
        ],
    ])


def _menu_quran_texte():
    return (
        "📖 *Coran*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Que veux-tu faire ?"
    )


def _menu_hijri():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌙 Date Hijri du jour", callback_data="hijri_today"),
            InlineKeyboardButton("📅 Fêtes à venir", callback_data="hijri_fetes"),
        ],
        [
            InlineKeyboardButton("🌙 Ramadan", callback_data="hijri_ramadan"),
        ],
        [
            InlineKeyboardButton("⬅️ Menu principal", callback_data="menu_back"),
        ],
    ])


def _menu_hijri_texte():
    return (
        "🌙 *Calendrier Hijri*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Que veux-tu consulter ?"
    )


def _menu_rappel():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Activer", callback_data="menu_rappel_on"),
            InlineKeyboardButton("❌ Désactiver", callback_data="menu_rappel_off"),
        ],
        [
            InlineKeyboardButton("ℹ️ État actuel", callback_data="menu_rappel_etat"),
        ],
        [
            InlineKeyboardButton("⬅️ Menu principal", callback_data="menu_back"),
        ],
    ])


def _menu_rappel_texte():
    return (
        "🔔 *Rappel quotidien*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Le rappel t'envoie un hadith automatiquement.\n\n"
        "Choisis une option :"
    )


# ============================================================
#   Commandes /start et /menu
# ============================================================

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/menu → affiche le menu principal."""
    await update.message.reply_text(
        _menu_texte(),
        reply_markup=_menu_principal(),
        parse_mode="Markdown"
    )


# ============================================================
#   Callbacks
# ============================================================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur les boutons du menu."""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Retour au menu principal
    if data == "menu_back":
        try:
            await query.edit_message_text(
                _menu_texte(),
                reply_markup=_menu_principal(),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        return

    # Menu Coran
    if data == "menu_quran":
        await query.edit_message_text(
            _menu_quran_texte(),
            reply_markup=_menu_quran(),
            parse_mode="Markdown"
        )
        return

    # Menu Hijri
    if data == "menu_hijri":
        await query.edit_message_text(
            _menu_hijri_texte(),
            reply_markup=_menu_hijri(),
            parse_mode="Markdown"
        )
        return

    # Notifications
    if data == "menu_notif":
        from bot.handlers.notifications import _keyboard, _texte
        await query.edit_message_text(
            _texte(),
            reply_markup=_keyboard(query.from_user.id),
            parse_mode="Markdown"
        )
        return

    # Aide
    if data == "menu_help":
        from bot.handlers.menu import _menu_principal  # évite le circular
        # On délègue à help_command
        from main import help_command
        await help_command(update, context)
        return

    # --- Actions directes ---

    # Hadith
    if data == "menu_hadith":
        from bot.handlers.hadith import hadith_command
        await hadith_command(update, context)
        return

    # Prière
    if data == "menu_priere":
        from bot.handlers.priere import priere_command
        await priere_command(update, context)
        return

    # Qibla
    if data == "menu_qibla":
        from bot.handlers.qibla import qibla_command
        await qibla_command(update, context)
        return

    # Bibliothèque
    if data == "menu_biblio":
        from bot.handlers.bibliotheque import bibliotheque_command
        await bibliotheque_command(update, context)
        return

    # Ville
    if data == "menu_ville":
        from bot.handlers.priere import ville_command
        await ville_command(update, context)
        return

    # Langue
    if data == "menu_langue":
        from bot.handlers.langue import langue_command
        await langue_command(update, context)
        return

    # --- Actions du sous-menu Coran ---

    if data == "menu_quran_random":
        import random
        from bot.handlers.quran import QURAN, send_sourate
        sourate = random.choice(QURAN.get("fr", []))
        await send_sourate(update, sourate)
        return

    if data == "menu_quran_liste":
        from bot.handlers.quran import liste_command
        await liste_command(update, context)
        return

    if data == "menu_quran_search":
        await query.edit_message_text(
            "🔍 *Recherche dans le Coran*\n\n"
            "Tape : `/recherche <mot>`\n\n"
            "Exemple : `/recherche miséricorde`",
            parse_mode="Markdown"
        )
        return

    if data == "menu_quran_verset":
        await query.edit_message_text(
            "📖 *Verset précis*\n\n"
            "Tape : `/verset <sourate>:<verset>`\n\n"
            "Exemple : `/verset 2:255`",
            parse_mode="Markdown"
        )
        return

    # --- Actions du sous-menu Rappel ---

    if data == "menu_rappel_on":
        from bot.database import set_rappel
        set_rappel(query.from_user.id, 1)
        await query.edit_message_text(
            "✅ Rappel *activé*. Tu recevras un hadith chaque jour.",
            parse_mode="Markdown"
        )
        return

    if data == "menu_rappel_off":
        from bot.database import set_rappel
        set_rappel(query.from_user.id, 0)
        await query.edit_message_text(
            "❌ Rappel *désactivé*.",
            parse_mode="Markdown"
        )
        return

    if data == "menu_rappel_etat":
        from bot.database import get_user
        row = get_user(query.from_user.id)
        etat = "activé ✅" if (row and row[0] == 1) else "désactivé ❌"
        await query.edit_message_text(
            f"🔔 État actuel : *{etat}*",
            parse_mode="Markdown"
        )
        return