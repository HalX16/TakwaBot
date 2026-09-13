import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database import get_langue


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "quran"
)

QURAN = {}
for code, fichier in [("fr", "quran.json"), ("en", "quran_en.json")]:
    path = os.path.join(DATA_DIR, fichier)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            QURAN[code] = json.load(f)
        print(f"📖 Coran chargé ({code}) : {len(QURAN[code])} sourates")
    else:
        QURAN[code] = []
        print(f"⚠️ Fichier manquant : {fichier}")


def get_quran(langue: str):
    if langue in QURAN and QURAN[langue]:
        return QURAN[langue]
    return QURAN.get("fr", [])


def _normalize(text: str) -> str:
    return text.lower().replace("-", "").replace("'", "").replace(" ", "")


def find_sourate(query: str, quran_data):
    if query.isdigit():
        num = int(query)
        if 1 <= num <= 114:
            return quran_data[num - 1]
        return None
    q = _normalize(query)
    for s in quran_data:
        if _normalize(s["name"]) == q or _normalize(s["transliteration"]) == q:
            return s
    return None


async def _reply(update: Update, text: str, **kwargs):
    if update.callback_query:
        await update.callback_query.message.reply_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)


# ============================================================
#   Construction du message d'une sourate
# ============================================================

def build_sourate_message(sourate: dict):
    """Retourne (header, full_message)."""
    header = (
        f"📖 *Sourate {sourate['id']} — {sourate['transliteration']}*\n"
        f"_{sourate['name']}_\n"
        f"📍 {sourate['type']} • {sourate['total_verses']} versets\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    body = ""
    for v in sourate["verses"]:
        body += f"*{v['id']}.* {v['text']}\n"
        body += f"_{v['translation']}_\n\n"
    return header, header + body


def keyboard_sourate(sid: int):
    """Boutons Précédente / Menu / Suivante + Soutenir + Menu principal."""
    prev_id = 114 if sid == 1 else sid - 1
    next_id = 1 if sid == 114 else sid + 1
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"⬅️ {prev_id}", callback_data=f"sur_{prev_id}"),
            InlineKeyboardButton("📚 Menu", callback_data="sur_menu"),
            InlineKeyboardButton(f"{next_id} ➡️", callback_data=f"sur_{next_id}"),
        ],
        [
            InlineKeyboardButton("💝 Soutenir", callback_data="don_menu"),
            InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back"),
        ]
    ])


async def send_sourate(update: Update, sourate: dict, edit: bool = False):
    """Envoie ou édite le message d'une sourate."""
    header, full = build_sourate_message(sourate)
    kb = keyboard_sourate(sourate["id"])

    # Si trop long → on envoie juste le header avec boutons
    if len(full) > 4096:
        if edit and update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    header, reply_markup=kb, parse_mode="Markdown"
                )
            except Exception:
                await _reply(update, header, reply_markup=kb, parse_mode="Markdown")
        else:
            await _reply(update, header, reply_markup=kb, parse_mode="Markdown")
        # Puis les versets en plusieurs messages
        chunk = ""
        for v in sourate["verses"]:
            part = f"*{v['id']}.* {v['text']}\n_{v['translation']}_\n\n"
            if len(chunk) + len(part) > 4000:
                await _reply(update, chunk, parse_mode="Markdown")
                chunk = ""
            chunk += part
        if chunk:
            await _reply(update, chunk, parse_mode="Markdown")
        return

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                full, reply_markup=kb, parse_mode="Markdown"
            )
            return
        except Exception:
            pass  # si trop long ou erreur → nouveau message

    await _reply(update, full, reply_markup=kb, parse_mode="Markdown")


# ============================================================
#   /sourate
# ============================================================

async def sourate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    langue = get_langue(user_id)
    quran_data = get_quran(langue)

    if not context.args:
        await _reply(update,
            "📖 Utilisation :\n"
            "`/sourate 1` → Al-Fatiha\n"
            "`/sourate 112` → Al-Ikhlas\n\n"
            "💡 Tape `/liste` pour voir les 114 sourates.",
            parse_mode="Markdown"
        )
        return

    query = " ".join(context.args)
    sourate = find_sourate(query, quran_data)
    if not sourate:
        await _reply(update, f"❌ Sourate `{query}` introuvable.",
                     parse_mode="Markdown")
        return

    await send_sourate(update, sourate)


# ============================================================
#   Callback : navigation entre sourates
# ============================================================

async def sourate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    langue = get_langue(user_id)
    quran_data = get_quran(langue)

    data = query.data  # "sur_1", "sur_menu", etc.

    if data == "sur_menu":
        await liste_command(update, context)
        return

    try:
        sid = int(data.split("_")[1])
    except (IndexError, ValueError):
        return

    if not (1 <= sid <= 114):
        return

    sourate = quran_data[sid - 1]
    await send_sourate(update, sourate, edit=True)


# ============================================================
#   /liste
# ============================================================

async def liste_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    langue = get_langue(user_id)
    quran_data = get_quran(langue)

    lines = ["📚 *Les 114 sourates du Coran*\n"]
    for s in quran_data:
        lines.append(f"`{s['id']:>3}` — {s['transliteration']} ({s['name']})")

    text = "\n".join(lines)
    for i in range(0, len(text), 4000):
        await _reply(update, text[i:i + 4000], parse_mode="Markdown")


# ============================================================
#   /verset
# ============================================================

async def verset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    langue = get_langue(user_id)
    quran_data = get_quran(langue)

    if not context.args:
        await _reply(update,
            "📖 Utilisation : `/verset <sourate>:<verset>`\n\n"
            "Exemples :\n"
            "`/verset 2:255` → Aya al-Kursi\n"
            "`/verset 112:1` → Al-Ikhlas v.1",
            parse_mode="Markdown"
        )
        return

    arg = context.args[0]
    if ":" not in arg:
        await _reply(update, "⚠️ Format invalide. Exemple : `/verset 2:255`",
                     parse_mode="Markdown")
        return

    try:
        s_num, v_num = arg.split(":")
        s_num, v_num = int(s_num), int(v_num)
    except ValueError:
        await _reply(update, "⚠️ Les numéros doivent être entiers.")
        return

    if not (1 <= s_num <= 114):
        await _reply(update, "⚠️ Numéro de sourate : 1 à 114.")
        return

    sourate = quran_data[s_num - 1]
    if not (1 <= v_num <= sourate["total_verses"]):
        await _reply(update,
            f"⚠️ La sourate contient {sourate['total_verses']} versets.")
        return

    v = sourate["verses"][v_num - 1]
    msg = (
        f"📖 *{sourate['transliteration']} {s_num}:{v_num}*\n"
        f"_({sourate['name']})_\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{v['text']}\n\n"
        f"_{v['translation']}_"
    )
    await _reply(update, msg, parse_mode="Markdown")


# ============================================================
#   /recherche
# ============================================================

async def recherche_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    langue = get_langue(user_id)
    quran_data = get_quran(langue)

    if not context.args:
        await _reply(update,
            "🔍 Utilisation : `/recherche <mot>`\n\n"
            "Exemples :\n"
            "`/recherche miséricorde`\n"
            "`/recherche patience`",
            parse_mode="Markdown"
        )
        return

    mot = " ".join(context.args).strip()
    if len(mot) < 3:
        await _reply(update, "⚠️ Mot de 3 caractères minimum.")
        return

    mot_lower = mot.lower()
    resultats = []
    for s in quran_data:
        for v in s["verses"]:
            if mot_lower in v["translation"].lower():
                resultats.append((s["id"], s["transliteration"], v["id"], v["translation"]))
                if len(resultats) >= 15:
                    break
        if len(resultats) >= 15:
            break

    if not resultats:
        await _reply(update, f"❌ Aucun verset contenant *{mot}*.",
                     parse_mode="Markdown")
        return

    header = (
        f"🔍 *Résultats pour : {mot}*\n"
        f"_{len(resultats)} verset(s) (max 15)_\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    body = ""
    for s_id, s_trans, v_id, translation in resultats:
        texte = translation if len(translation) < 200 else translation[:200] + "..."
        body += f"*{s_trans} {s_id}:{v_id}*\n_{texte}_\n\n"

    full = header + body
    if len(full) <= 4096:
        await _reply(update, full, parse_mode="Markdown")
    else:
        await _reply(update, header, parse_mode="Markdown")
        chunk = ""
        for s_id, s_trans, v_id, translation in resultats:
            texte = translation if len(translation) < 200 else translation[:200] + "..."
            part = f"*{s_trans} {s_id}:{v_id}*\n_{texte}_\n\n"
            if len(chunk) + len(part) > 4000:
                await _reply(update, chunk, parse_mode="Markdown")
                chunk = ""
            chunk += part
        if chunk:
            await _reply(update, chunk, parse_mode="Markdown")