from telegram.ext import ContextTypes
from bot.database import get_users_with_rappel, get_langue
from bot.handlers.hadith import get_hadith, format_hadith


async def send_daily_hadith(context: ContextTypes.DEFAULT_TYPE):
    """Envoie un hadith à tous les utilisateurs ayant le rappel actif."""
    users = get_users_with_rappel()
    print(f"📤 Envoi quotidien à {len(users)} utilisateur(s)...")

    for user_id in users:
        try:
            langue = get_langue(user_id)
            h = get_hadith(langue)
            message = format_hadith(h)

            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"⚠️ Impossible d'envoyer à {user_id} : {e}")