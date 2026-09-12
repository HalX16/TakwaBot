from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes


# Montants disponibles en Stars
MONTANTS = [5, 20, 50, 100]


async def don_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/don → affiche les boutons de donation."""
    keyboard = []

    for montant in MONTANTS:
        label = f"⭐ Donner {montant} Stars"
        callback_data = f"don_{montant}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💝 *Soutenez TakwaBot !*\n\n"
        "Vos dons nous aident à couvrir les frais de serveur "
        "et à améliorer le bot.\n\n"
        "🤲 JazakAllah khair pour votre soutien !",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def don_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère le clic sur un bouton de don."""
    query = update.callback_query
    await query.answer()

    # Récupère le montant depuis le callback_data (ex: "don_20")
    data = query.data  # "don_20"
    try:
        montant = int(data.split("_")[1])
    except (IndexError, ValueError):
        await query.message.reply_text("❌ Montant invalide.")
        return

    # Envoie la facture Stars
    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=f"Soutien TakwaBot — {montant} Stars",
        description=f"Merci de soutenir TakwaBot avec {montant} Stars. "
                    f"Votre don aide à couvrir les frais du serveur.",
        payload=f"don_{montant}_{query.from_user.id}",
        provider_token="",  # Vide pour Telegram Stars
        currency="XTR",     # Devise Telegram Stars
        prices=[LabeledPrice(label="Don", amount=montant)]
    )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Valide le paiement avant qu'il ne soit effectué."""
    query = update.pre_checkout_query
    # On accepte toujours (pas de stock à vérifier ici)
    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirme le paiement réussi."""
    payment = update.message.successful_payment
    montant = payment.total_amount
    user = update.effective_user

    await update.message.reply_text(
        f"✅ *Don reçu !*\n\n"
        f"Merci {user.first_name} pour ton soutien de *{montant} Stars* ! 🎉\n\n"
        f"🤲 Qu'Allah te récompense pour ta générosité.\n\n"
        f"Ton don aidera à améliorer TakwaBot in shaa Allah.",
        parse_mode="Markdown"
    )

    # Log simple dans la console (pour toi)
    print(f"💰 Don reçu : {user.id} ({user.first_name}) — {montant} Stars")