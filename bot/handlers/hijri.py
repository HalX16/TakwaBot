from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from hijri_converter import Gregorian, Hijri


# ============================================================
#   Événements islamiques (jour/mois Hijri)
# ============================================================

EVENEMENTS = {
    (1, 1):   "🎉 Nouvel An islamique (1 Muharram)",
    (1, 10):  "🕯️ Achoura (10 Muharram)",
    (3, 12):  "🌙 Mawlid — Naissance du Prophète ﷺ (12 Rabi' al-Awwal)",
    (7, 27):  "✨ Isra et Miraj (27 Rajab)",
    (8, 15):  "🌕 Nuit de la Mi-Cha'ban (15 Cha'ban)",
    (9, 1):   "🌙 Début du Ramadan (1 Ramadan)",
    (9, 27):  "✨ Nuit du Destin — Laylat al-Qadr (27 Ramadan)",
    (10, 1):  "🎉 Aïd al-Fitr (1 Shawwal)",
    (12, 9):  "🕋 Jour d'Arafat (9 Dhul Hijjah)",
    (12, 10): "🐑 Aïd al-Adha (10 Dhul Hijjah)",
    (12, 29): "🌙 Veille du Nouvel An islamique",
}


MOIS_HIJRI = [
    "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani",
    "Jumada al-Ula", "Jumada al-Akhira", "Rajab", "Cha'ban",
    "Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah"
]


def _reply_sync(update, text, **kwargs):
    """Version sync pour utiliser dans du code non-async."""
    pass


async def _reply(update: Update, text: str, **kwargs):
    if update.callback_query:
        await update.callback_query.message.reply_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)


def hijri_aujourd_hui():
    """Retourne (jour, mois, annee) hijri d'aujourd'hui."""
    g = Gregorian.today()
    h = g.to_hijri()
    return h.day, h.month, h.year


def hijri_depuis_date(d: datetime):
    g = Gregorian(d.year, d.month, d.day)
    h = g.to_hijri()
    return h.day, h.month, h.year


def date_gregorienne_depuis_hijri(j: int, m: int, a: int):
    """Retourne la date grégorienne correspondante."""
    try:
        h = Hijri(a, m, j)
        g = h.to_gregorian()
        return datetime(g.year, g.month, g.day)
    except Exception:
        return None


# ============================================================
#   /hijri
# ============================================================

async def hijri_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    j, m, a = hijri_aujourd_hui()
    mois_nom = MOIS_HIJRI[m - 1]

    aujourd_hui = datetime.now()
    date_gr = aujourd_hui.strftime("%d/%m/%Y")

    msg = (
        f"🌙 *Date Hijri du jour*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📅 *{j} {mois_nom} {a} AH*\n"
        f"🗓️ ({date_gr} grégorien)\n\n"
    )

    # Événement éventuel aujourd'hui
    event = EVENEMENTS.get((m, j))
    if event:
        msg += f"\n🎊 *Aujourd'hui :* {event}\n"
    else:
        # Cherche un événement proche (±3 jours)
        for delta in range(-3, 4):
            if delta == 0:
                continue
            date_proche = aujourd_hui + timedelta(days=delta)
            jp, mp, ap = hijri_depuis_date(date_proche)
            ev = EVENEMENTS.get((mp, jp))
            if ev:
                jour_rel = "aujourd'hui" if delta == 0 else (
                    f"dans {delta} jour(s)" if delta > 0 else f"il y a {abs(delta)} jour(s)"
                )
                msg += f"\n📌 *Événement proche :* {ev} ({jour_rel})\n"
                break

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Fêtes à venir", callback_data="hijri_fetes")],
        [InlineKeyboardButton("🌙 Ramadan", callback_data="hijri_ramadan")],
    ])

    await _reply(update, msg, reply_markup=kb, parse_mode="Markdown")


# ============================================================
#   /fetes
# ============================================================

async def fetes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    aujourd_hui = datetime.now()
    j_auj, m_auj, a_auj = hijri_aujourd_hui()

    prochains = []

    # Cherche chaque événement sur 2 ans
    for (jm, mm), label in EVENEMENTS.items():
        for annee in [a_auj, a_auj + 1, a_auj + 2]:
            date_gr = date_gregorienne_depuis_hijri(jm, mm, annee)
            if date_gr and date_gr.date() >= aujourd_hui.date():
                prochains.append((date_gr, label))
                break

    prochains.sort(key=lambda x: x[0])
    prochains = prochains[:8]

    msg = (
        "🕌 *Prochaines fêtes islamiques*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for date_gr, label in prochains:
        delta = (date_gr.date() - aujourd_hui.date()).days
        if delta == 0:
            quand = "🔴 *Aujourd'hui !*"
        elif delta == 1:
            quand = "🟠 Demain"
        elif delta <= 30:
            quand = f"dans {delta} jours"
        else:
            mois = delta // 30
            quand = f"dans ~{mois} mois"

        date_str = date_gr.strftime("%d/%m/%Y")
        msg += f"{label}\n📅 {date_str} — _{quand}_\n\n"

    msg += "⚠️ _Les dates peuvent varier selon l'observation de la lune._"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 Date Hijri du jour", callback_data="hijri_today")],
        [InlineKeyboardButton("🌙 Ramadan", callback_data="hijri_ramadan")],
    ])

    await _reply(update, msg, reply_markup=kb, parse_mode="Markdown")


# ============================================================
#   /ramadan
# ============================================================

async def ramadan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    aujourd_hui = datetime.now()
    j_auj, m_auj, a_auj = hijri_aujourd_hui()

    # Est-on en Ramadan ?
    if m_auj == 9:
        jours_restants = 30 - j_auj  # approximation
        msg = (
            "🌙 *Ramadan Mubarak !*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 Nous sommes au *{j_auj} Ramadan {a_auj} AH*\n\n"
            f"⏳ Environ *{jours_restants} jours* restants avant Aïd al-Fitr.\n\n"
            f"🤲 Qu'Allah accepte ton jeûne et tes prières."
        )
    else:
        # Prochain Ramadan
        annee_cible = a_auj if m_auj < 9 else a_auj + 1
        date_ramadan = date_gregorienne_depuis_hijri(1, 9, annee_cible)

        if not date_ramadan:
            await _reply(update, "⚠️ Impossible de calculer la date du Ramadan.")
            return

        delta = (date_ramadan.date() - aujourd_hui.date()).days

        if delta < 0:
            date_ramadan = date_gregorienne_depuis_hijri(1, 9, annee_cible + 1)
            delta = (date_ramadan.date() - aujourd_hui.date()).days

        mois_restants = delta // 30
        jours_restants = delta % 30

        msg = (
            "🌙 *Prochain Ramadan*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📅 Début estimé : *{date_ramadan.strftime('%d/%m/%Y')}*\n"
            f"⏳ Dans *{delta} jours* "
            f"({mois_restants} mois et {jours_restants} jours)\n\n"
            f"🤲 Qu'Allah nous permettre d'atteindre ce mois béni."
        )

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Fêtes à venir", callback_data="hijri_fetes")],
        [InlineKeyboardButton("🌙 Date Hijri du jour", callback_data="hijri_today")],
    ])

    await _reply(update, msg, reply_markup=kb, parse_mode="Markdown")


# ============================================================
#   Callbacks
# ============================================================

async def hijri_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # "hijri_fetes", "hijri_today", "hijri_ramadan"

    if data == "hijri_fetes":
        await fetes_command(update, context)
    elif data == "hijri_today":
        await hijri_command(update, context)
    elif data == "hijri_ramadan":
        await ramadan_command(update, context)