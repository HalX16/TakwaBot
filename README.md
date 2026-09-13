# 🕌 TakwaBot

> Bot Telegram islamique — Coran, hadiths, horaires de prière, Qibla, calendrier Hijri et plus.

**TakwaBot** est un assistant spirituel complet pour la communauté musulmane sur Telegram. Il combine des rappels religieux authentiques et des outils pratiques du quotidien, le tout dans une interface simple et intuitive.

---

## ✨ Fonctionnalités

### 📖 Coran
- Lire n'importe quelle sourate (114 disponibles)
- Lire un verset précis (ex: Aya al-Kursi `/verset 2:255`)
- Rechercher un mot-clé dans le Coran
- Navigation entre sourates avec boutons ⬅️ ➡️

### 🕋 Hadiths
- Hadith aléatoire (Sahih al-Bukhari, Sahih Muslim)
- Multilingue : français (local), arabe et anglais (API authentique)

### 📿 Prière & Qibla
- Heures de prière pour ~150 villes
- Calcul selon la méthode française (UOIF)
- Direction de la Qibla avec angle précis

### 🌙 Calendrier Hijri
- Date Hijri du jour
- Prochaines fêtes islamiques
- Compte à rebours pour Ramadan

### 🔔 Notifications
- 4 rappels quotidiens configurables : 8h, 13h, 18h, 21h

### 📚 Bibliothèque
- Liens vers livres islamiques gratuits et légaux

### 💝 Soutien
- Dons via Telegram Stars

---

## 🚀 Installation

### Prérequis
- Python 3.13+
- Git
- Un bot Telegram (créé via @BotFather)

### Étapes

1. Cloner le repo : `git clone https://github.com/HalX16/TakwaBot.git`
2. Entrer dans le dossier : `cd TakwaBot`
3. Créer l'environnement virtuel : `python -m venv venv`
4. Activer l'environnement (Windows) : `venv\Scripts\activate`
5. Installer les dépendances : `pip install -r requirements.txt`
6. Créer un fichier `.env` avec : `BOT_TOKEN=ton_token_ici`
7. Télécharger `quran.json` et `quran_en.json` depuis https://github.com/risan/quran-json et les placer dans `data/quran/`
8. Lancer le bot : `python main.py`

---

## 📖 Commandes disponibles

| Commande | Description |
|---|---|
| `/start` | Menu principal avec boutons |
| `/menu` | Menu principal |
| `/sourate` | Lire une sourate (numéro ou nom) |
| `/verset` | Lire un verset précis (ex: 2:255) |
| `/recherche` | Rechercher dans le Coran |
| `/liste` | Les 114 sourates |
| `/hadith` | Hadith aléatoire |
| `/notifications` | Configurer les rappels |
| `/ville` | Choisir sa ville |
| `/location` | Saisie libre de ville |
| `/priere` | Heures de prière |
| `/qibla` | Direction de la Qibla |
| `/hijri` | Date Hijri |
| `/fetes` | Prochaines fêtes |
| `/ramadan` | Compte à rebours |
| `/bibliotheque` | Livres islamiques |
| `/langue` | Changer la langue (FR/EN/AR) |
| `/don` | Soutenir le projet |
| `/partager` | Partager le bot |
| `/help` | Aide complète |

---

## 🛠️ Technologies

- **Python 3.13**
- **python-telegram-bot** v21+
- **SQLite**
- **prayer-times-calculator**
- **hijri-converter**
- **fawazahmed0/hadith-api**

---

## 🚀 Déploiement

Le bot est prévu pour être déployé sur **Railway** (24h/24).

1. Créer un projet depuis ce repo GitHub
2. Ajouter la variable `BOT_TOKEN`
3. Monter un volume sur `/data` (persistance SQLite)
4. Railway détecte automatiquement `Procfile` et `.python-version`

---

## 🤝 Contribution

Les contributions sont **les bienvenues** !

- Signaler un bug via Issues
- Proposer des améliorations via Pull Requests
- Ajouter des villes, hadiths ou livres

---

## 📄 Licence

Ce projet est sous licence **MIT** — voir le fichier LICENSE pour plus de détails.

---

## 🤲 Remerciements

- **@HalX16** — Créateur du projet
- **fawazahmed0** — API hadiths
- **risan** — Données du Coran en JSON
- La communauté musulmane sur Telegram

---

## 📞 Contact

- **Telegram** : @tkwaHBot
- **GitHub** : HalX16

---

**Qu'Allah bénisse ce projet et le rende utile à la communauté.** 🤲