from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes


MONTANTS = [5, 20, 50, 100]


def _keyboard_montants():
    buttons = []
    for montant in MONTANTS:
        buttons.append([
            InlineKeyboardButton(
                f"⭐ Donner {montant} Stars",
                callback_data=f"don_{montant}"
            )
        ])
    return InlineKeyboardMarkup(buttons)


async def don_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/don → affiche les boutons de donation."""
    await update.message.reply_text(
        "💝 *Soutenez TakwaBot !*\n\n"
        "Vos dons nous aident à couvrir les frais de serveur "
        "et à améliorer le bot.\n\n"
        "🤲 JazakAllah khair pour votre soutien !",
        reply_markup=_keyboard_montants(),
        parse_mode="Markdown"
    )


async def don_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bouton 'Soutenir TakwaBot' → affiche le menu de dons."""
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "💝 *Soutenez TakwaBot !*\n\n"
        "Vos dons nous aident à couvrir les frais de serveur "
        "et à améliorer le bot.\n\n"
        "🤲 JazakAllah khair pour votre soutien !",
        reply_markup=_keyboard_montants(),
        parse_mode="Markdown"
    )


async def don_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère le clic sur un bouton de don."""
    query = update.callback_query
    await query.answer()

    data = query.data  # "don_20"
    try:
        montant = int(data.split("_")[1])
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Montant invalide.")
        return

    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=f"Soutien TakwaBot — {montant} Stars",
        description=f"Merci de soutenir TakwaBot avec {montant} Stars.",
        payload=f"don_{montant}_{query.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Don", amount=montant)]
    )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    montant = payment.total_amount
    user = update.effective_user

    from bot.handlers.partage import keyboard_partage

    await update.message.reply_text(
        f"✅ *Don reçu !*\n\n"
        f"Merci {user.first_name} pour ton soutien de *{montant} Stars* ! 🎉\n\n"
        f"🤲 Qu'Allah te récompense pour ta générosité.\n\n"
        f"💡 Tu peux aussi nous aider en partageant TakwaBot 👇",
        reply_markup=keyboard_partage(),
        parse_mode="Markdown"
    )

    print(f"💰 Don reçu : {user.id} ({user.first_name}) — {montant} Stars")