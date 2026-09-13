from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def bouton_menu():
    """Retourne le bouton 'Menu principal'."""
    return InlineKeyboardButton("🏠 Menu principal", callback_data="menu_back")


def ajouter_menu(keyboard_buttons: list) -> InlineKeyboardMarkup:
    """Ajoute le bouton menu à la fin d'une liste de boutons."""
    keyboard_buttons.append([bouton_menu()])
    return InlineKeyboardMarkup(keyboard_buttons)