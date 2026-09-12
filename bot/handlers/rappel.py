from telegram import Update
from telegram.ext import ContextTypes
from bot.database import set_rappel, get_user


async def rappel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/rappel on|off → active/désactive le rappel quotidien."""
    user_id = update.effective_user.id

    if not context.args:
        row = get_user(user_id)
        etat = "activé ✅" if (row and row[0] == 1) else "désactivé ❌"
        await update.message.reply_text(
            f"🔔 Rappel quotidien actuellement *{etat}*.\n\n"
            f"Utilise :\n"
            f"`/rappel on` → activer\n"
            f"`/rappel off` → désactiver",
            parse_mode="Markdown"
        )
        return

    arg = context.args[0].lower()
    if arg in ("on", "activer", "oui"):
        set_rappel(user_id, 1)
        await update.message.reply_text(
            "✅ Rappel activé. Tu recevras un hadith chaque jour à *8h*.",
            parse_mode="Markdown"
        )
    elif arg in ("off", "desactiver", "non"):
        set_rappel(user_id, 0)
        await update.message.reply_text(
            "❌ Rappel désactivé."
        )
    else:
        await update.message.reply_text(
            "⚠️ Utilise `/rappel on` ou `/rappel off`.",
            parse_mode="Markdown"
        )