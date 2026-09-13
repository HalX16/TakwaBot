import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


BOOKS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "books.json"
)

BOOKS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "books"
)

with open(BOOKS_PATH, "r", encoding="utf-8") as f:
    BOOKS = json.load(f)


# Catégories pour le filtrage
CATEGORIES = ["Coran", "Hadiths", "Invocations", "Croyance", "Histoire"]


async def _reply(update: Update, text: str, **kwargs):
    if update.callback_query:
        await update.callback_query.message.reply_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)


def _keyboard_categories():
    buttons = []
    row = []
    for cat in CATEGORIES:
        row.append(InlineKeyboardButton(cat, callback_data=f"book_cat_{cat}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("📚 Tous les livres", callback_data="book_cat_ALL")])
    buttons.append([InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back")])
    return InlineKeyboardMarkup(buttons)

def _keyboard_books(categorie: str):
    """Affiche les livres d'une catégorie."""
    if categorie == "ALL":
        livres = BOOKS
    else:
        livres = [b for b in BOOKS if b["categorie"] == categorie]

    buttons = []
    for b in livres:
        # Marqueur : 📥 si PDF dispo, 🔗 si lien externe seulement
        emoji = "📥" if b.get("disponible") else "🔗"
        buttons.append([
            InlineKeyboardButton(f"{emoji} {b['titre']}", callback_data=f"book_{b['id']}")
        ])
    buttons.append([InlineKeyboardButton("⬅️ Catégories", callback_data="book_back")])
    return InlineKeyboardMarkup(buttons), livres


def _keyboard_book_detail(book_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Retour", callback_data="book_back")],
        [InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back")]
    ])


# ============================================================
#   /bibliotheque
# ============================================================

async def bibliotheque_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Affiche les catégories de livres."""
    await _reply(update,
        "📚 *Bibliothèque islamique*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choisis une catégorie :",
        reply_markup=_keyboard_categories(),
        parse_mode="Markdown"
    )


async def bibliotheque_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics dans la bibliothèque."""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Retour aux catégories
    if data == "book_back":
        try:
            await query.edit_message_text(
                "📚 *Bibliothèque islamique*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Choisis une catégorie :",
                reply_markup=_keyboard_categories(),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        return

    # Choix d'une catégorie
    if data.startswith("book_cat_"):
        cat = data.replace("book_cat_", "")
        kb, livres = _keyboard_books(cat)

        if not livres:
            await query.edit_message_text(
                f"❌ Aucun livre dans la catégorie *{cat}*.",
                reply_markup=_keyboard_categories(),
                parse_mode="Markdown"
            )
            return

        titre = "Tous les livres" if cat == "ALL" else cat
        await query.edit_message_text(
            f"📚 *{titre}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{len(livres)} livre(s) disponible(s).\n\n"
            f"📥 = téléchargement direct\n"
            f"🔗 = lien externe",
            reply_markup=kb,
            parse_mode="Markdown"
        )
        return

    # Détail d'un livre
    if data.startswith("book_"):
        book_id = data.replace("book_", "")
        book = next((b for b in BOOKS if b["id"] == book_id), None)

        if not book:
            await query.answer("❌ Livre introuvable", show_alert=True)
            return

        # Si PDF local disponible → on l'envoie
        if book.get("disponible") and book.get("fichier"):
            filepath = os.path.join(BOOKS_DIR, book["fichier"])
            if os.path.exists(filepath):
                await query.message.reply_text(
                    f"📖 *{book['titre']}*\n"
                    f"_{book['auteur']}_\n\n"
                    f"Envoi du fichier en cours...",
                    parse_mode="Markdown"
                )
                try:
                    with open(filepath, "rb") as f:
                        await query.message.reply_document(
                            document=f,
                            filename=book["fichier"],
                            caption=f"📖 *{book['titre']}*\n_{book['auteur']}_",
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    await query.message.reply_text(f"❌ Erreur d'envoi : {e}")
                return

        # Sinon → lien externe
        texte = (
            f"📖 *{book['titre']}*\n"
            f"✍️ _{book['auteur']}_\n"
            f"🌍 Langue : {book['langue'].upper()}\n"
            f"📂 Catégorie : {book['categorie']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{book['description']}\n\n"
        )

        if book.get("url_externe"):
            texte += f"🔗 [Télécharger depuis la source]({book['url_externe']})"
        else:
            texte += "⚠️ _Fichier non disponible pour l'instant._"

        await query.edit_message_text(
            texte,
            reply_markup=_keyboard_book_detail(book_id),
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        return