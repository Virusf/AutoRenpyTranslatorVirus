# Exemples d'utilisation

## Exemple 1 : Traduction basique

```bash
# Traduction automatique en français avec Google Translate
python AutoRenpyTranslator.py
```

## Exemple 2 : Traduction vers l'espagnol

```bash
# Créer d'abord le dossier de traduction espagnole avec renpy-translator
# Puis lancer la traduction
python AutoRenpyTranslator.py --lang es --translation-lang spanish
```

## Exemple 3 : Utilisation avec LibreTranslate

```bash
# 1. Installer LibreTranslate
pip install libretranslate

# 2. Lancer le serveur LibreTranslate
libretranslate --host 0.0.0.0 --port 5000

# 3. Lancer la traduction
python AutoRenpyTranslator.py --service libretranslate
```

## Exemple 4 : Traduction d'un fichier spécifique

```bash
# Traduire seulement le fichier principal
python AutoRenpyTranslator.py --file game/tl/french/script.rpy
```

## Exemple 5 : Projet avec structure personnalisée

```bash
# Si votre dossier game est dans un sous-dossier
python AutoRenpyTranslator.py --path MonJeu/game
```

## Workflow complet avec renpy-translator

### Étape 1 : Extraction des fichiers

```bash
# Cloner renpy-translator
git clone https://github.com/anonymousException/renpy-translator

# Aller dans le dossier de votre jeu Ren'Py
cd MonJeuRenpy

# Extraire les fichiers de traduction
python /chemin/vers/renpy-translator/extract.py --lang french
```

### Étape 2 : Traduction automatique

```bash
# Cloner auto-renpy-translator
git clone https://github.com/votre-username/auto-renpy-translator

# Copier les fichiers dans le projet
cp auto-renpy-translator/AutoRenpyTranslator.* .

# Lancer la traduction
python AutoRenpyTranslator.py
```

### Étape 3 : Test et ajustement

```bash
# Lancer le jeu Ren'Py pour tester
# Faire des corrections manuelles si nécessaire
# Relancer la traduction si besoin
```

## Langues supportées

| Code | Langue | Exemple |
|------|---------|---------|
| `fr` | Français | `--lang fr --translation-lang french` |
| `es` | Espagnol | `--lang es --translation-lang spanish` |
| `de` | Allemand | `--lang de --translation-lang german` |
| `it` | Italien | `--lang it --translation-lang italian` |
| `pt` | Portugais | `--lang pt --translation-lang portuguese` |
| `ru` | Russe | `--lang ru --translation-lang russian` |
| `ja` | Japonais | `--lang ja --translation-lang japanese` |
| `ko` | Coréen | `--lang ko --translation-lang korean` |
| `zh` | Chinois | `--lang zh --translation-lang chinese` |

## Conseils d'utilisation

### Pour de meilleurs résultats :

1. **Utilisez LibreTranslate** pour les gros projets (pas de limite de taux)
2. **Faites des sauvegardes** régulières (automatique mais prudence)
3. **Testez fréquemment** pour détecter les problèmes tôt
4. **Corrigez manuellement** les passages importants après traduction
5. **Utilisez Google Translate** pour les petits projets (plus simple)

### Structure recommandée :

```
MonJeuRenpy/
├── game/
│   ├── script.rpy
│   ├── characters.rpy
│   └── tl/
│       ├── french/
│       │   ├── script.rpy      # Fichiers extraits
│       │   └── characters.rpy  # par renpy-translator
│       └── spanish/
│           ├── script.rpy      # Autres langues
│           └── characters.rpy
├── AutoRenpyTranslator.py
├── AutoRenpyTranslator.bat
└── requirements.txt
```