from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes
)
from datetime import time

from config import BOT_TOKEN
from bot.database import init_db, register_user
from bot.handlers.quran import (
    sourate_command, liste_command, verset_command,
    recherche_command, sourate_callback
)
from bot.handlers.hadith import hadith_command, hadith_callback
from bot.handlers.rappel import rappel_command
from bot.handlers.priere import (
    location_command, priere_command, ville_command,
    ville_callback, action_callback
)
from bot.handlers.qibla import qibla_command
from bot.handlers.dons import (
    don_command, don_callback, pre_checkout, successful_payment,
    don_menu_callback
)
from bot.handlers.langue import langue_command, langue_callback
from bot.handlers.hijri import (
    hijri_command, fetes_command, ramadan_command, hijri_callback
)
from bot.handlers.bibliotheque import (
    bibliotheque_command, bibliotheque_callback
)
from bot.handlers.notifications import (
    notifications_command, notifications_callback
)
from bot.handlers.menu import menu_command, menu_callback
from bot.daily_job import send_matin, send_midi, send_soir, send_nuit


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username)
    await menu_command(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back")],
        [InlineKeyboardButton("💝 Soutenir TakwaBot", callback_data="don_menu")],
    ])

    await update.message.reply_text(
        "📖 *Toutes les commandes TakwaBot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "*📖 Coran*\n"
        "*/sourate <n°|nom>* → Lire une sourate\n"
        "*/verset X:Y* → Verset précis (ex: 2:255)\n"
        "*/recherche <mot>* → Chercher dans le Coran\n"
        "*/liste* → Les 114 sourates\n\n"
        "*🕋 Hadith*\n"
        "*/hadith* → Hadith aléatoire\n"
        "*/rappel on|off* → Rappel quotidien\n"
        "*/notifications* → 4 rappels par jour\n\n"
        "*📿 Prière & Qibla*\n"
        "*/ville* → Choisir ta ville (boutons)\n"
        "*/location <ville>* → Saisie libre\n"
        "*/priere* → Heures de prière\n"
        "*/qibla* → Direction de la Qibla\n\n"
        "*🌙 Calendrier*\n"
        "*/hijri* → Date Hijri du jour\n"
        "*/fetes* → Prochaines fêtes\n"
        "*/ramadan* → Compte à rebours\n\n"
        "*📚 Autres*\n"
        "*/bibliotheque* → Livres islamiques\n"
        "*/langue* → FR / EN / AR\n"
        "*/don* → Soutenir le projet\n"
        "*/menu* → Menu principal\n\n"
        "💡 _Astuce : utilise le menu pour cliquer directement !_",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sourate", sourate_command))
    app.add_handler(CommandHandler("verset", verset_command))
    app.add_handler(CommandHandler("recherche", recherche_command))
    app.add_handler(CommandHandler("liste", liste_command))
    app.add_handler(CommandHandler("hadith", hadith_command))
    app.add_handler(CommandHandler("rappel", rappel_command))
    app.add_handler(CommandHandler("notifications", notifications_command))
    app.add_handler(CommandHandler("location", location_command))
    app.add_handler(CommandHandler("ville", ville_command))
    app.add_handler(CommandHandler("priere", priere_command))
    app.add_handler(CommandHandler("qibla", qibla_command))
    app.add_handler(CommandHandler("hijri", hijri_command))
    app.add_handler(CommandHandler("fetes", fetes_command))
    app.add_handler(CommandHandler("ramadan", ramadan_command))
    app.add_handler(CommandHandler("bibliotheque", bibliotheque_command))
    app.add_handler(CommandHandler("langue", langue_command))
    app.add_handler(CommandHandler("don", don_command))

    # Callbacks
    app.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^menu_"))
    app.add_handler(CallbackQueryHandler(notifications_callback, pattern=r"^notif_"))
    app.add_handler(CallbackQueryHandler(don_callback, pattern=r"^don_\d+$"))
    app.add_handler(CallbackQueryHandler(don_menu_callback, pattern=r"^don_menu$"))
    app.add_handler(CallbackQueryHandler(langue_callback, pattern=r"^lang_"))
    app.add_handler(CallbackQueryHandler(hadith_callback, pattern=r"^hadith_"))
    app.add_handler(CallbackQueryHandler(ville_callback, pattern=r"^ville_"))
    app.add_handler(CallbackQueryHandler(action_callback, pattern=r"^action_"))
    app.add_handler(CallbackQueryHandler(sourate_callback, pattern=r"^sur_"))
    app.add_handler(CallbackQueryHandler(hijri_callback, pattern=r"^hijri_"))
    app.add_handler(CallbackQueryHandler(bibliotheque_callback, pattern=r"^book_"))

    # Paiement
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    # Jobs quotidiens (4 créneaux)
    if app.job_queue:
        app.job_queue.run_daily(send_matin, time=time(hour=8,  minute=0), name="pub_matin")
        app.job_queue.run_daily(send_midi,  time=time(hour=13, minute=0), name="pub_midi")
        app.job_queue.run_daily(send_soir,  time=time(hour=18, minute=0), name="pub_soir")
        app.job_queue.run_daily(send_nuit,  time=time(hour=21, minute=0), name="pub_nuit")
        print("⏰ 4 rappels quotidiens programmés (8h, 13h, 18h, 21h).")

    print("✅ TakwaBot v1.4 — Notifications multiples actives.")
    app.run_polling()


if __name__ == "__main__":
    main()