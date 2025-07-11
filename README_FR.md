# Auto Renpy Translator

Un outil automatique de traduction pour les projets Ren'Py qui traduit automatiquement tous les fichiers `.rpy` de traduction extraits.

## 📋 Prérequis

- Python 3.6 ou supérieur
- Un projet Ren'Py avec les fichiers de traduction extraits (`game/tl/french/` par exemple)
- Connexion Internet (pour Google Translate) ou instance locale de LibreTranslate

## 🚀 Installation et utilisation

### Étape 1 : Extraire les fichiers de traduction

Avant d'utiliser cet outil, vous devez extraire les fichiers de traduction de votre projet Ren'Py :

1. Clonez et utilisez **renpy-translator** :
   ```bash
   git clone https://github.com/anonymousException/renpy-translator
   ```

2. Suivez les instructions du projet pour extraire les fichiers `.rpy` dans `game/tl/[langue]/`

---

### Étape 2 : Utilisation de l'auto-traducteur

1. Clonez ce projet dans le dossier de votre jeu :
   ```bash
   git clone https://github.com/votre-utilisateur/auto-renpy-translator
   ```

2. Placez les fichiers dans la racine du projet :
   ```
   MonJeuRenpy/
   ├── game/
   │   ├── tl/
   │   │   └── french/
   │   ├── change_language_entrance.rpy       # Généré automatiquement
   │   ├── set_default_language_at_startup.rpy # Généré automatiquement
   │   └── ...
   ├── AutoRenpyTranslator.py
   └── AutoRenpyTranslator.bat
   ```

3. Lancez la traduction :

   **Windows** :
   ```bash
   AutoRenpyTranslator.bat
   ```

   **Linux/Mac** :
   ```bash
   python AutoRenpyTranslator.py
   ```

---

## ⚙️ Options avancées

### Commandes disponibles

```bash
# Traduction avec Google Translate
python AutoRenpyTranslator.py

# Utiliser LibreTranslate local
python AutoRenpyTranslator.py --service libretranslate

# Spécifier le chemin vers le dossier game
python AutoRenpyTranslator.py --path /chemin/vers/game

# Changer la langue cible
python AutoRenpyTranslator.py --lang es --translation-lang spanish

# Traduire un seul fichier
python AutoRenpyTranslator.py --file game/tl/french/script.rpy
```

### Paramètres disponibles

- `--path` : chemin vers `game` (détection automatique sinon)
- `--lang` : code de langue cible (`fr`, `es`, `ja`, etc.)
- `--translation-lang` : nom du dossier de langue (`french`, `spanish`, etc.)
- `--service` : `google` (par défaut) ou `libretranslate`
- `--libretranslate-url` : URL vers LibreTranslate local (`http://localhost:5000`)
- `--file` : fichier `.rpy` unique à traduire

---

## 🌐 Services de traduction

### Google Translate (par défaut)

- ✅ Gratuit
- ❗ Limité à 5000 caractères par requête
- ⚠ Peut être bloqué par Google après usage intensif

### LibreTranslate (recommandé pour une utilisation massive)

```bash
pip install libretranslate
libretranslate --host 0.0.0.0 --port 5000
```

Puis lancez :

```bash
python AutoRenpyTranslator.py --service libretranslate
```

---

## 🛠 Fonctionnalités

- ✅ Détection automatique du dossier `game`
- ✅ Préserve les balises Ren'Py (`{b}`, `{w}`, `{i}`, etc.)
- ✅ Sauvegarde automatique avant toute traduction
- ✅ Barre de progression
- ✅ Traduction ligne par ligne avec gestion des erreurs
- ✅ Génération automatique des fichiers :
  - `change_language_entrance.rpy`
  - `set_default_language_at_startup.rpy`

---

## 📁 Structure typique

```
MonJeuRenpy/
├── game/
│   ├── tl/
│   │   └── french/
│   │       ├── script.rpy
│   │       ├── characters.rpy
│   │       └── ...
│   ├── change_language_entrance.rpy
│   ├── set_default_language_at_startup.rpy
├── backup_translations_YYYYMMDD_HHMMSS/
├── AutoRenpyTranslator.py
└── AutoRenpyTranslator.bat
```

---

## 🔐 Sécurité et fiabilité

- 💾 **Sauvegarde automatique** dans un dossier horodaté
- 🛡 **Pas de modification des identifiants techniques** (`old:xxxxx`)
- ❌ **{w} supprimés** pour éviter des erreurs de position
- 🧠 **Préserve le style et les balises Ren'Py**

---

## 📜 Licence

Ce projet est sous licence **Creative Commons BY-NC 4.0** :
- ✅ Modification et partage autorisés
- ❌ Usage commercial interdit
- ❌ Revente interdite

Voir le fichier `LICENSE` pour plus d’informations.

---

## 🙏 Remerciements

- [renpy-translator](https://github.com/anonymousException/renpy-translator)
- [googletrans](https://github.com/ssut/googletrans)
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)

---

## ✨ Contribution

Vous pouvez :
- Signaler des bugs ou des traductions incorrectes
- Proposer des améliorations
- Ajouter de nouvelles options
- Améliorer la compatibilité avec d'autres services
