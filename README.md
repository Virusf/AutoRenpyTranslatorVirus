# Auto Renpy Translator

Un outil automatique de traduction pour les projets Ren'Py qui traduit automatiquement tous les fichiers de traduction générés.

## 📋 Prérequis

- Python 3.6 ou supérieur
- Un projet Ren'Py avec des fichiers de traduction extraits
- Connexion Internet (pour Google Translate) ou LibreTranslate local

## 🚀 Installation et Utilisation

### Étape 1 : Extraction des fichiers de traduction

Avant d'utiliser cet outil, vous devez d'abord extraire les fichiers de traduction de votre projet Ren'Py :

1. Téléchargez et utilisez **renpy-translator** :
   ```bash
   git clone https://github.com/anonymousException/renpy-translator
   ```

2. Suivez les instructions du projet renpy-translator pour extraire les fichiers `.rpy` de traduction dans le dossier `game/tl/[langue]/`

### Étape 2 : Utilisation de l'Auto-traducteur

1. **Clonez ce projet** dans le répertoire de votre jeu Ren'Py :
   ```bash
   git clone https://github.com/votre-username/auto-renpy-translator
   ```

2. **Placez les fichiers** dans le dossier racine de votre projet Ren'Py :
   ```
   MonJeuRenpy/
   ├── game/
   │   ├── tl/
   │   │   └── french/  # Fichiers .rpy extraits par renpy-translator
   │   └── ...
   ├── AutoRenpyTranslator.py
   └── AutoRenpyTranslator.bat
   ```

3. **Lancez la traduction** :
   
   **Sur Windows :**
   ```bash
   AutoRenpyTranslator.bat
   ```
   
   **Sur Linux/Mac :**
   ```bash
   python AutoRenpyTranslator.py
   ```

## ⚙️ Options avancées

### Utilisation en ligne de commande

```bash
# Traduction automatique (Google Translate)
python AutoRenpyTranslator.py

# Avec LibreTranslate local
python AutoRenpyTranslator.py --service libretranslate

# Spécifier un chemin personnalisé
python AutoRenpyTranslator.py --path /chemin/vers/game

# Traduire vers une autre langue
python AutoRenpyTranslator.py --lang es --translation-lang spanish

# Traduire un fichier spécifique
python AutoRenpyTranslator.py --file game/tl/french/script.rpy
```

### Paramètres disponibles

- `--path` : Chemin vers le dossier `game` (détection automatique par défaut)
- `--lang` : Code de langue cible (par défaut: `fr`)
- `--translation-lang` : Nom du dossier de langue (par défaut: `french`)
- `--service` : Service de traduction (`google` ou `libretranslate`)
- `--libretranslate-url` : URL de LibreTranslate (par défaut: `http://localhost:5000`)
- `--file` : Traduire un fichier spécifique

## 🔧 Services de traduction

### Google Translate (par défaut)
- **Avantages** : Gratuit, aucune configuration requise
- **Inconvénients** : Limité à 5000 caractères par requête, peut être bloqué en cas d'usage intensif

### LibreTranslate
- **Avantages** : Illimité, privé, rapide
- **Inconvénients** : Nécessite une installation locale

#### Installation de LibreTranslate

```bash
# Avec pip
pip install libretranslate

# Lancer le serveur
libretranslate --host 0.0.0.0 --port 5000

# Puis utiliser l'auto-traducteur
python AutoRenpyTranslator.py --service libretranslate
```

## 📁 Structure du projet

```
MonJeuRenpy/
├── game/
│   ├── tl/
│   │   └── french/           # Fichiers .rpy à traduire
│   │       ├── script.rpy
│   │       ├── characters.rpy
│   │       └── ...
│   ├── change_language_entrance.rpy    # Généré automatiquement
│   ├── set_default_language_at_startup.rpy  # Généré automatiquement
│   └── ...
├── backup_translations_YYYYMMDD_HHMMSS/  # Sauvegarde automatique
├── AutoRenpyTranslator.py
└── AutoRenpyTranslator.bat
```

## 🛡️ Sécurité

- **Sauvegarde automatique** : Une sauvegarde est créée automatiquement avant chaque traduction
- **Préservation des balises** : Les balises Ren'Py (`{b}`, `{i}`, `{w}`, etc.) sont préservées
- **Gestion des erreurs** : Les erreurs n'interrompent pas le processus

## 🌐 Langues supportées

Le script supporte toutes les langues disponibles dans Google Translate. Exemples :

- `fr` : Français
- `es` : Espagnol
- `de` : Allemand
- `it` : Italien
- `pt` : Portugais
- `ru` : Russe
- `ja` : Japonais
- `ko` : Coréen
- `zh` : Chinois

## 🔍 Fonctionnalités

- ✅ **Détection automatique** du dossier `game`
- ✅ **Traduction intelligente** qui préserve les balises Ren'Py
- ✅ **Sauvegarde automatique** avant traduction
- ✅ **Gestion des erreurs** robuste
- ✅ **Support des gros fichiers** (découpage automatique)
- ✅ **Installation automatique** des dépendances
- ✅ **Génération automatique** des fichiers de configuration de langue
- ✅ **Barre de progression** pour suivre l'avancement

## 🐛 Dépannage

### Problèmes courants

**Erreur "Dossier game introuvable"**
- Vérifiez que vous êtes dans le bon répertoire
- Utilisez `--path` pour spécifier le chemin manuellement

**Erreur Google Translate**
- Vérifiez votre connexion Internet
- Essayez d'attendre quelques minutes (limite de taux)
- Passez à LibreTranslate : `--service libretranslate`

**Erreur LibreTranslate**
- Vérifiez que LibreTranslate est installé et lancé
- Testez l'URL : `curl http://localhost:5000/languages`

## 📝 Workflow complet

1. **Préparer le projet Ren'Py** avec les fichiers sources
2. **Extraire les traductions** avec [renpy-translator](https://github.com/anonymousException/renpy-translator)
3. **Cloner cet outil** dans le dossier du projet
4. **Lancer la traduction** avec `AutoRenpyTranslator.bat`
5. **Tester le jeu** avec les nouvelles traductions
6. **Ajuster si nécessaire** et relancer

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Ajouter de nouvelles fonctionnalités
- Améliorer la documentation

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [renpy-translator](https://github.com/anonymousException/renpy-translator) pour l'extraction des fichiers
- [googletrans](https://github.com/ssut/googletrans) pour l'API Google Translate
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) pour l'alternative libre

## 📧 Support

Si vous rencontrez des problèmes, n'hésitez pas à ouvrir une issue sur GitHub.