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

# ============================================================
#   Villes par région
# ============================================================

VILLES_PAR_REGION = {
    "france": [
        "Paris", "Marseille", "Lyon", "Toulouse", "Lille", "Bordeaux",
        "Nice", "Strasbourg", "Nantes", "Montpellier", "Rennes", "Reims",
        "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes",
        "Villeurbanne", "Clermont-Ferrand", "Le Mans", "Aix-en-Provence",
        "Brest", "Tours", "Amiens", "Limoges", "Annecy", "Perpignan",
        "Besançon", "Metz", "Orléans", "Rouen", "Mulhouse", "Caen",
        "Nancy", "Argenteuil", "Montreuil", "Avignon", "Poitiers",
        "Dunkerque", "Versailles", "Colombes", "Asnières-sur-Seine",
        "Créteil", "Aubervilliers", "Aulnay-sous-Bois", "Saint-Denis",
    ],
    "europe": [
        "Bruxelles", "Anvers", "Liège", "Gand", "Charleroi",
        "Genève", "Zurich", "Lausanne", "Berne", "Bâle",
        "Londres", "Manchester", "Birmingham", "Glasgow", "Édimbourg", "Liverpool",
        "Madrid", "Barcelone", "Valence", "Séville", "Málaga",
        "Rome", "Milan", "Naples", "Turin",
        "Berlin", "Munich", "Francfort", "Hambourg", "Cologne",
        "Amsterdam", "Rotterdam", "La Haye",
        "Lisbonne", "Porto", "Vienne", "Stockholm", "Oslo",
        "Copenhague", "Helsinki", "Dublin",
    ],
    "maghreb": [
        "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger",
        "Agadir", "Meknès", "Oujda", "Kénitra",
        "Alger", "Oran", "Constantine", "Annaba", "Sétif",
        "Tunis", "Sfax", "Sousse", "Kairouan",
        "Tripoli", "Nouakchott",
    ],
    "moyen_orient": [
        "Istanbul", "Ankara", "Izmir",
        "La Mecque", "Médine", "Riyad", "Djeddah",
        "Dubaï", "Abu Dhabi", "Doha", "Koweït", "Manama", "Mascate",
        "Le Caire", "Alexandrie",
        "Amman", "Beyrouth", "Damas", "Bagdad",
        "Jérusalem", "Gaza", "Téhéran",
    ],
    "afrique": [
        "Dakar", "Touba", "Bamako", "Abidjan", "Conakry",
        "Ouagadougou", "Niamey", "Cotonou", "Lomé",
        "Yaoundé", "Douala", "Libreville", "Kinshasa", "Brazzaville",
        "Khartoum", "Mogadiscio", "Djibouti",
    ],
    "ameriques": [
        "Montréal", "Toronto", "Ottawa", "Vancouver", "Québec",
        "New York", "Los Angeles", "Chicago", "Houston", "Miami",
        "Détroit", "Washington", "Boston",
        "Mexico", "São Paulo", "Buenos Aires",
    ],
    "asie": [
        "Pékin", "Shanghai", "Tokyo", "Séoul", "Jakarta",
        "Kuala Lumpur", "Singapour", "Karachi", "Lahore", "Islamabad",
        "Delhi", "Mumbai", "Dacca", "Kaboul",
    ],
}

REGIONS_LABELS = {
    "france": "🇫🇷 France",
    "europe": "🇪🇺 Europe",
    "maghreb": "🇲🇦 Maghreb",
    "moyen_orient": "🕌 Moyen-Orient",
    "afrique": "🌍 Afrique",
    "ameriques": "🌎 Amériques",
    "asie": "🌏 Asie",
}


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
    # Bouton "Plus de villes"
    buttons.append([
        InlineKeyboardButton("🌍 Plus de villes", callback_data="ville_more")
    ])
    return InlineKeyboardMarkup(buttons)


def _keyboard_regions():
    """Clavier des régions."""
    buttons = []
    row = []
    for key, label in REGIONS_LABELS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"region_{key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton("⬅️ Retour", callback_data="ville_back")
    ])
    return InlineKeyboardMarkup(buttons)


def _keyboard_villes_region(region_key: str):
    """Clavier des villes d'une région."""
    villes = VILLES_PAR_REGION.get(region_key, [])
    buttons = []
    row = []
    for label in villes:
        cb = "ville_" + label.lower().replace(" ", "_").replace("'", "")
        row.append(InlineKeyboardButton(label, callback_data=cb))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton("⬅️ Régions", callback_data="ville_more")
    ])
    return InlineKeyboardMarkup(buttons)


async def ville_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    row = get_ville(user_id)
    actuelle = f"*{row[0]}*" if row and row[0] else "_aucune_"

    await _reply(update,
        f"📍 *Choisis ta ville*\n\n"
        f"Ville actuelle : {actuelle}\n\n"
        f"👇 Clique sur une ville ci-dessous.\n\n"
        f"💡 *Ta ville n'est pas dans la liste ?*\n"
        f"Tape simplement : `/location NomDeTaVille`\n"
        f"Exemple : `/location Strasbourg`",
        reply_markup=_keyboard_villes(),
        parse_mode="Markdown"
    )


async def ville_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Bouton "Plus de villes" → affiche les régions
    if data == "ville_more":
        await query.edit_message_text(
            "🌍 *Plus de villes*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choisis une région :\n\n"
            "💡 *Ta ville n'est pas dans la liste ?*\n"
            "Tape directement `/location NomDeTaVille`",
            reply_markup=_keyboard_regions(),
            parse_mode="Markdown"
        )
        return

    # Bouton "Retour" depuis les régions → retour aux villes populaires
    if data == "ville_back":
        user_id = query.from_user.id
        row = get_ville(user_id)
        actuelle = f"*{row[0]}*" if row and row[0] else "_aucune_"

        await query.edit_message_text(
            f"📍 *Choisis ta ville*\n\n"
            f"Ville actuelle : {actuelle}\n\n"
            f"👇 Clique sur une ville ci-dessous.\n\n"
            f"💡 *Ta ville n'est pas dans la liste ?*\n"
            f"Tape : `/location NomDeTaVille`",
            reply_markup=_keyboard_villes(),
            parse_mode="Markdown"
        )
        return

    # Bouton "Région" → affiche les villes de la région
    if data.startswith("region_"):
        region_key = data.replace("region_", "")
        if region_key not in VILLES_PAR_REGION:
            await query.answer("❌ Région inconnue", show_alert=True)
            return

        label = REGIONS_LABELS.get(region_key, region_key)
        await query.edit_message_text(
            f"{label}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Choisis ta ville :",
            reply_markup=_keyboard_villes_region(region_key),
            parse_mode="Markdown"
        )
        return

    # Bouton "Ville" → enregistre la ville
    if data.startswith("ville_"):
        key = data.replace("ville_", "").replace("_", " ").replace("'", "")
        ville = find_ville(key)
        if not ville:
            await query.answer("❌ Ville introuvable", show_alert=True)
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
        return


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