from telegram import Update
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
    don_command, don_callback, pre_checkout, successful_payment
)
from bot.handlers.langue import langue_command, langue_callback
from bot.handlers.hijri import (
    hijri_command, fetes_command, ramadan_command, hijri_callback
)
from bot.handlers.bibliotheque import (
    bibliotheque_command, bibliotheque_callback
)
from bot.daily_job import send_daily_hadith


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username)

    await update.message.reply_text(
        "🕌 Assalamou alaykoum !\n\n"
        "Bienvenue sur *TakwaBot*, ton compagnon spirituel.\n\n"
        "📖 *Commandes disponibles :*\n"
        "/sourate <n°|nom> - Lire une sourate\n"
        "/verset X:Y - Lire un verset précis\n"
        "/recherche <mot> - Chercher dans le Coran\n"
        "/liste - Voir les 114 sourates\n"
        "/hadith - Un hadith du jour\n"
        "/rappel on|off - Activer/désactiver le rappel\n"
        "/ville - Choisir ta ville (boutons)\n"
        "/priere - Heures de prière\n"
        "/qibla - Direction de la Qibla\n"
        "/hijri - Date Hijri du jour\n"
        "/fetes - Prochaines fêtes islamiques\n"
        "/ramadan - Compte à rebours Ramadan\n"
        "/bibliotheque - Livres islamiques\n"
        "/langue - Changer la langue (boutons)\n"
        "/don - Soutenir le projet\n"
        "/help - Aide",
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Aide TakwaBot*\n\n"
        "*/sourate 1* → Al-Fatiha (avec boutons ⬅️ ➡️)\n"
        "*/verset 2:255* → Aya al-Kursi\n"
        "*/recherche patience* → Versets sur la patience\n"
        "*/hadith* → Hadith aléatoire (bouton 🔄)\n"
        "*/rappel on|off* → Rappel quotidien\n"
        "*/ville* → Choisir ta ville (boutons)\n"
        "*/priere* → Heures de prière\n"
        "*/qibla* → Direction de la Qibla\n"
        "*/hijri* → Date Hijri du jour\n"
        "*/fetes* → Prochaines fêtes islamiques\n"
        "*/ramadan* → Compte à rebours Ramadan\n"
        "*/bibliotheque* → Livres islamiques\n"
        "*/langue* → Changer la langue (boutons)\n"
        "*/don* → Soutenir le projet",
        parse_mode="Markdown"
    )


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sourate", sourate_command))
    app.add_handler(CommandHandler("verset", verset_command))
    app.add_handler(CommandHandler("recherche", recherche_command))
    app.add_handler(CommandHandler("liste", liste_command))
    app.add_handler(CommandHandler("hadith", hadith_command))
    app.add_handler(CommandHandler("rappel", rappel_command))
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

    # Callbacks (boutons)
    app.add_handler(CallbackQueryHandler(don_callback, pattern=r"^don_"))
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

    # Job quotidien
    if app.job_queue:
        app.job_queue.run_daily(
            send_daily_hadith,
            time=time(hour=8, minute=0),
            name="daily_hadith"
        )
        print("⏰ Rappel quotidien programmé à 8h00.")

    print("✅ TakwaBot v1.2 — Bibliothèque ajoutée.")
    app.run_polling()


if __name__ == "__main__":
    main()