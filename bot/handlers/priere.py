import json
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from prayer_times_calculator import PrayerTimesCalculator
from bot.database import set_ville, get_ville


VILLES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "villes.json"
)

with open(VILLES_PATH, "r", encoding="utf-8") as f:
    VILLES = json.load(f)


def _normalize(text: str) -> str:
    return (
        text.lower().strip()
        .replace("-", " ").replace("'", " ")
        .replace("é", "e").replace("è", "e").replace("ê", "e")
        .replace("à", "a").replace("î", "i").replace("ô", "o")
        .replace("û", "u").replace("ç", "c")
    )


def find_ville(query: str):
    q = _normalize(query)
    for key, v in VILLES.items():
        if _normalize(key) == q or _normalize(v["nom"]) == q:
            return v
    for key, v in VILLES.items():
        if q in _normalize(key) or q in _normalize(v["nom"]):
            return v
    return None


async def _reply(update: Update, text: str, **kwargs):
    """Répond soit à un message normal, soit à un clic de bouton."""
    if update.callback_query:
        await update.callback_query.message.reply_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)


# ============================================================
#   /location <ville>  — saisie libre
# ============================================================

async def location_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not context.args:
        row = get_ville(user_id)
        if row and row[0]:
            await _reply(update,
                f"📍 Ta ville actuelle : *{row[0]}*\n\n"
                f"Pour la changer : `/location <ville>`",
                parse_mode="Markdown"
            )
        else:
            await _reply(update,
                "📍 Aucune ville enregistrée.\n\n"
                "Utilise `/ville` pour choisir par boutons.",
                parse_mode="Markdown"
            )
        return

    query = " ".join(context.args)
    ville = find_ville(query)
    if not ville:
        await _reply(update,
            f"❌ Ville `{query}` introuvable.",
            parse_mode="Markdown"
        )
        return

    set_ville(user_id, ville["nom"], ville["lat"], ville["lon"])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📿 Voir les heures de prière", callback_data="action_priere")],
        [InlineKeyboardButton("🧭 Direction de la Qibla", callback_data="action_qibla")],
        [InlineKeyboardButton("📍 Changer de ville", callback_data="action_ville")],
    ])

    await _reply(update,
        f"✅ Ville enregistrée : *{ville['nom']}* ({ville['pays']})\n\n"
        f"Que veux-tu faire maintenant ?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
#   /ville  — choix par boutons
# ============================================================

VILLES_POPULAIRES = [
    "Paris", "Marseille", "Lyon", "Lille",
    "Bordeaux", "Bruxelles", "Genève", "Londres",
    "Montréal", "Casablanca", "Alger", "Tunis",
    "Istanbul", "La Mecque", "Médine", "Le Caire",
    "Dakar", "Abidjan",
]


def _keyboard_villes():
    buttons = []
    row = []
    for label in VILLES_POPULAIRES:
        cb = "ville_" + label.lower().replace(" ", "_")
        row.append(InlineKeyboardButton(label, callback_data=cb))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


async def ville_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    row = get_ville(user_id)
    actuelle = f"*{row[0]}*" if row and row[0] else "_aucune_"

    await _reply(update,
        f"📍 *Choisis ta ville*\n\n"
        f"Ville actuelle : {actuelle}\n\n"
        f"👇 Clique sur une ville.",
        reply_markup=_keyboard_villes(),
        parse_mode="Markdown"
    )


async def ville_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data.split("_", 1)[1].replace("_", " ")
    ville = find_ville(key)
    if not ville:
        await query.edit_message_text("❌ Ville introuvable.")
        return

    user_id = query.from_user.id
    set_ville(user_id, ville["nom"], ville["lat"], ville["lon"])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📿 Voir les heures de prière", callback_data="action_priere")],
        [InlineKeyboardButton("🧭 Direction de la Qibla", callback_data="action_qibla")],
        [InlineKeyboardButton("📍 Changer de ville", callback_data="action_ville")],
    ])

    await query.edit_message_text(
        f"✅ Ville enregistrée : *{ville['nom']}* ({ville['pays']})\n\n"
        f"Que veux-tu faire maintenant ?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ============================================================
#   /priere
# ============================================================

async def priere_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        calc = PrayerTimesCalculator(
            latitude=lat, longitude=lon,
            calculation_method="france", date=today
        )
        times = calc.fetch_prayer_times()
    except Exception as e:
        await _reply(update, f"❌ Erreur de calcul : {e}")
        return

    def clean(t):
        return t.split(" ")[0] if t else "—"

    fajr = clean(times.get("Fajr"))
    dhuhr = clean(times.get("Dhuhr"))
    asr = clean(times.get("Asr"))
    maghrib = clean(times.get("Maghrib"))
    isha = clean(times.get("Isha"))

    maintenant = datetime.now()
    prieres = {"Fajr": fajr, "Dhuhr": dhuhr, "Asr": asr,
               "Maghrib": maghrib, "Isha": isha}
    prochaine = None
    for nom, heure in prieres.items():
        try:
            h, m = map(int, heure.split(":"))
            dt = maintenant.replace(hour=h, minute=m, second=0, microsecond=0)
            if dt > maintenant:
                prochaine = (nom, heure, dt)
                break
        except (ValueError, AttributeError):
            continue

    if not prochaine:
        try:
            h, m = map(int, fajr.split(":"))
            dt = (maintenant + timedelta(days=1)).replace(
                hour=h, minute=m, second=0, microsecond=0)
            prochaine = ("Fajr (demain)", fajr, dt)
        except (ValueError, AttributeError):
            prochaine = None

    date_fr = maintenant.strftime("%d/%m/%Y")
    msg = f"📿 *Heures de prière pour {ville}*\n_{date_fr}_\n━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🌅 Fajr    : `{fajr}`\n"
    msg += f"☀️ Dhuhr   : `{dhuhr}`\n"
    msg += f"🌇 Asr     : `{asr}`\n"
    msg += f"🌙 Maghrib : `{maghrib}`\n"
    msg += f"🌃 Isha    : `{isha}`\n\n"

    if prochaine:
        nom, heure, dt = prochaine
        delta = dt - maintenant
        total_min = int(delta.total_seconds() // 60)
        h_rest = total_min // 60
        m_rest = total_min % 60
        msg += f"⏳ Prochaine : *{nom}* à `{heure}` (dans {h_rest}h{m_rest:02d})"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Actualiser", callback_data="action_priere")],
        [InlineKeyboardButton("🧭 Qibla", callback_data="action_qibla")],
        [InlineKeyboardButton("📍 Changer de ville", callback_data="action_ville")],
    ])

    await _reply(update, msg, reply_markup=keyboard, parse_mode="Markdown")


# ============================================================
#   Callbacks d'action (boutons Prière / Qibla / Ville)
# ============================================================

async def action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # "action_priere", "action_qibla", "action_ville"

    if data == "action_priere":
        await priere_command(update, context)
    elif data == "action_qibla":
        # Import local pour éviter les imports circulaires
        from bot.handlers.qibla import qibla_command
        await qibla_command(update, context)
    elif data == "action_ville":
        await ville_command(update, context)