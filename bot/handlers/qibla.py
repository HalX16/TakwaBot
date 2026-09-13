import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.database import get_ville


KAABA_LAT = 21.4225
KAABA_LON = 39.8262


def calculer_qibla(lat: float, lon: float) -> float:
    lat1 = math.radians(lat)
    lat2 = math.radians(KAABA_LAT)
    dlon = math.radians(KAABA_LON - lon)
    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    angle = math.degrees(math.atan2(x, y))
    return (angle + 360) % 360


def direction_cardinale(angle: float) -> str:
    directions = [
        "Nord ⬆️", "Nord-Est ↗️", "Est ➡️", "Sud-Est ↘️",
        "Sud ⬇️", "Sud-Ouest ↙️", "Ouest ⬅️", "Nord-Ouest ↖️"
    ]
    idx = int((angle + 22.5) % 360 // 45)
    return directions[idx]


def fleche_emoji(angle: float) -> str:
    if angle < 22.5 or angle >= 337.5:
        return "⬆️"
    elif angle < 67.5:
        return "↗️"
    elif angle < 112.5:
        return "➡️"
    elif angle < 157.5:
        return "↘️"
    elif angle < 202.5:
        return "⬇️"
    elif angle < 247.5:
        return "↙️"
    elif angle < 292.5:
        return "⬅️"
    else:
        return "↖️"


async def _reply(update: Update, text: str, **kwargs):
    if update.callback_query:
        await update.callback_query.message.reply_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)


async def qibla_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    row = get_ville(user_id)

    if not row or not row[0]:
        await _reply(update,
            "📍 Tu n'as pas encore choisi de ville.\n\n"
            "Utilise `/ville`.",
            parse_mode="Markdown"
        )
        return

    ville, lat, lon = row
    angle = calculer_qibla(lat, lon)
    direction = direction_cardinale(angle)
    fleche = fleche_emoji(angle)

    msg = (
        f"🕋 *Direction de la Qibla*\n"
        f"📍 Depuis *{ville}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{fleche} *{angle:.1f}°* depuis le Nord\n"
        f"🧭 Direction : *{direction}*\n\n"
        f"💡 Oriente ton téléphone vers le Nord, "
        f"puis tourne de *{angle:.0f}°* vers la droite."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Recalculer", callback_data="action_qibla")],
        [InlineKeyboardButton("📿 Heures de prière", callback_data="action_priere")],
        [InlineKeyboardButton("📍 Changer de ville", callback_data="action_ville")],
        [InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back")],
    ])

    await _reply(update, msg, reply_markup=keyboard, parse_mode="Markdown")