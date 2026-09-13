import random
from telegram.ext import ContextTypes
from bot.database import get_users_with_pub, get_langue
from bot.handlers.hadith import get_hadith, format_hadith
from bot.handlers.quran import QURAN


# ============================================================
#   Textes fixes
# ============================================================

INVOCATIONS = [
    "🤲 *SubhanAllahi wa bihamdihi, SubhanAllahi al-'Adhim.*\n\n_« Gloire à Allah et louange à Lui, gloire à Allah le Très Grand. »_\n\n📚 Bukhari et Muslim",
    "🤲 *La ilaha illa Allah wahdahu la sharika lah, lahul-mulku wa lahul-hamdu wa huwa 'ala kulli shay'in qadir.*\n\n_« Il n'y a de divinité qu'Allah, Seul, sans associé. À Lui la royauté, à Lui la louange, et Il est capable de toute chose. »_\n\n📚 Bukhari et Muslim",
    "🤲 *Allahumma salli wa sallim 'ala nabiyyina Muhammad.*\n\n_« Ô Allah, prie et accorde la paix à notre Prophète Muhammad. »_",
    "🤲 *Astaghfirullah wa atubu ilayh.*\n\n_« Je demande pardon à Allah et je me repens à Lui. »_\n\n📚 Bukhari",
    "🤲 *Hasbunallahu wa ni'mal-wakil.*\n\n_« Allah nous suffit, et Il est le meilleur Garant. »_\n\n📚 Coran 3:173",
    "🤲 *Rabbi zidni 'ilma.*\n\n_« Seigneur, augmente ma science. »_\n\n📚 Coran 20:114",
    "🤲 *Allahumma inni as'aluka al-jannah wa a'udhu bika min an-nar.*\n\n_« Ô Allah, je Te demande le Paradis et je cherche refuge auprès de Toi contre l'Enfer. »_",
    "🤲 *SubhanAllah, wal-hamdulillah, wa la ilaha illa Allah, wallahu akbar.*\n\n_« Gloire à Allah, louange à Allah, il n'y a de divinité qu'Allah, Allah est le plus Grand. »_",
]


# ============================================================
#   Helpers
# ============================================================

def _verset_aleatoire():
    """Retourne un verset aléatoire du Coran (français)."""
    quran_data = QURAN.get("fr", [])
    if not quran_data:
        return None
    sourate = random.choice(quran_data)
    verset = random.choice(sourate["verses"])
    return sourate, verset


def _format_verset(sourate, verset):
    return (
        f"📖 *Verset du jour*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*{sourate['transliteration']} {sourate['id']}:{verset['id']}*\n\n"
        f"{verset['text']}\n\n"
        f"_{verset['translation']}_"
    )


def _format_invocation():
    return (
        f"🌙 *Invocation du soir*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{random.choice(INVOCATIONS)}"
    )


async def _send_to_users(context, user_ids: list, message_builder):
    """Envoie un message à une liste d'utilisateurs."""
    print(f"📤 Envoi à {len(user_ids)} utilisateur(s)...")
    for user_id in user_ids:
        try:
            langue = get_langue(user_id)
            message = await message_builder(user_id, langue)
            if message:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"⚠️ Impossible d'envoyer à {user_id} : {e}")


# ============================================================
#   Jobs quotidiens
# ============================================================

async def send_matin(context: ContextTypes.DEFAULT_TYPE):
    """8h — Hadith du matin."""
    users = get_users_with_pub("matin")

    async def builder(user_id, langue):
        h = get_hadith(langue)
        return format_hadith(h)

    await _send_to_users(context, users, builder)


async def send_midi(context: ContextTypes.DEFAULT_TYPE):
    """13h — Verset du jour."""
    users = get_users_with_pub("midi")

    async def builder(user_id, langue):
        result = _verset_aleatoire()
        if not result:
            return None
        sourate, verset = result
        return _format_verset(sourate, verset)

    await _send_to_users(context, users, builder)


async def send_soir(context: ContextTypes.DEFAULT_TYPE):
    """18h — Hadith du soir."""
    users = get_users_with_pub("soir")

    async def builder(user_id, langue):
        h = get_hadith(langue)
        return format_hadith(h)

    await _send_to_users(context, users, builder)


async def send_nuit(context: ContextTypes.DEFAULT_TYPE):
    """21h — Invocation du soir."""
    users = get_users_with_pub("nuit")

    async def builder(user_id, langue):
        return _format_invocation()

    await _send_to_users(context, users, builder)