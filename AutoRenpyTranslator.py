#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import argparse
import os
import shutil
from datetime import datetime
from typing import List
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def install_and_import(package_name, pip_name=None):
    """Installe et importe un package si nécessaire"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        return __import__(package_name)
    except ImportError:
        print(f"⚠ Installation de {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ {package_name} installé avec succès")
            return __import__(package_name)
        except subprocess.CalledProcessError as e:
            print(f"✗ Erreur lors de l'installation de {package_name}: {e}")
            print("Essayez d'installer manuellement avec:")
            print(f"pip install {pip_name}")
            sys.exit(1)

def safe_import():
    """Importe les modules requis avec installation automatique"""
    print("🔍 Vérification des dépendances...")
    requests = install_and_import('requests')
    tqdm      = install_and_import('tqdm') 
    try:
        from googletrans import Translator
        print("✓ googletrans déjà installé")
    except ImportError:
        print("⚠ Installation de googletrans...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0rc1"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            from googletrans import Translator
            print("✓ googletrans installé avec succès")
        except Exception as e:
            print(f"✗ Erreur avec googletrans: {e}")
            print("Essayez une version alternative:")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==3.1.0a0"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                from googletrans import Translator
                print("✓ googletrans (version alternative) installé")
            except Exception as e2:
                print(f"✗ Impossible d'installer googletrans: {e2}")
                print("Installation manuelle requise:")
                print("pip install googletrans==4.0.0rc1")
                sys.exit(1)
    return requests, Translator

# Importation avec installation auto
requests, Translator = safe_import()

from tqdm import tqdm

# Lock pour les affichages thread-safe
print_lock = threading.Lock()

def thread_safe_print(*args, **kwargs):
    """Fonction d'affichage thread-safe"""
    with print_lock:
        print(*args, **kwargs)

class RenpyAutoTranslator:
    def __init__(self, service='google', libretranslate_url='http://localhost:5000', max_workers=3):
        self.service = service
        self.libretranslate_url = libretranslate_url
        self.google_translator = None
        self.max_workers = max_workers

        if service == 'google':
            try:
                self.google_translator = Translator()
                self.google_translator.translate("test", dest='fr')
                print("✓ Google Translate connecté")
            except Exception as e:
                print(f"⚠ Problème avec Google Translate: {e}")
                print("Passage en mode LibreTranslate recommandé")
        self.google_char_limit = 5000

    def create_backup(self, source_path: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_translations_{timestamp}"
        if os.path.exists(source_path):
            print(f"💾 Création de la sauvegarde: {backup_path}")
            shutil.copytree(source_path, backup_path)
            print(f"✓ Sauvegarde créée: {backup_path}")
        else:
            print(f"ℹ Aucune traduction existante à sauvegarder")
        return backup_path
    
    def find_game_folder(self, start_path: str = ".") -> str:
        game_path = os.path.join(start_path, "game")
        if os.path.exists(game_path):
            return game_path
        for root, dirs, files in os.walk(start_path):
            if "game" in dirs:
                return os.path.join(root, "game")
        return None

    def get_translation_path(self, game_path: str, language: str) -> str:
        return os.path.join(game_path, 'tl', language)

    def find_rpy_files(self, path: str) -> List[str]:
        rpy_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.rpy'):
                    rpy_files.append(os.path.join(root, file))
        return rpy_files

    def translate_text(self, text: str, target_lang: str) -> str:
        if not text or not text.strip():
            return text
        if self.service == 'google':
            return self._translate_google(text, target_lang)
        elif self.service == 'libretranslate':
            return self._translate_libretranslate(text, target_lang)
        else:
            raise ValueError(f"Service de traduction non supporté: {self.service}")

    def _translate_google(self, text, target_lang):
        try:
            result = self.google_translator.translate(text, dest=target_lang)
            return result.text
        except Exception as e:
            thread_safe_print(f"❌ Erreur Google Translate : {e}")
            return text

    def _translate_libretranslate(self, text, target_lang):
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "q": text,
                "source": "auto",
                "target": target_lang,
                "format": "text"
            }
            response = requests.post(f"{self.libretranslate_url}/translate", headers=headers, json=data)
            return response.json()["translatedText"]
        except Exception as e:
            thread_safe_print(f"❌ Erreur LibreTranslate : {e}")
            return text

    def format_text(self, text: str) -> str:
        # Ajoute des espaces autour des crochets et des balises Ren'Py
        text = re.sub(r'(?<!\s)(?<=\w)\[', ' [', text)  # Espace avant [
        text = re.sub(r'\](?=\w)', '] ', text)          # Espace après ]

        # Ajoute des espaces autour des accolades {balise}
        text = re.sub(r'(?<!\s)(\{[^}]+\})', r' \1', text)  # Espace avant {xxx}
        text = re.sub(r'(\{[^}]+\})(?!\s)', r'\1 ', text)   # Espace après {xxx}

        return text

    def preserve_renpy_tags(self, text: str):
        """Préserve les balises Ren'Py et retours à la ligne avec numérotation séquentielle"""
        # Pattern plus complet pour capturer toutes les balises Ren'Py
        pattern = re.compile(r'(\{[^}]*\}|\\n|\\t|\\r|\[[^\]]*\])')
        tags = []
        
        def replacer(match):
            tag = match.group(0)
            tags.append(tag)
            # Utilise des marqueurs uniques avec espaces pour éviter les collisions
            return f' RENPYTAG{len(tags)-1}END '
        
        replaced = pattern.sub(replacer, text)
        return replaced, tags

    def restore_renpy_tags(self, translated: str, original_tags: List[str]):
        """Restaure les balises Ren'Py avec gestion robuste des erreurs"""
        if not original_tags:
            return translated

        # Pattern insensible à la casse, avec espaces tolérés
        pattern_tag = re.compile(r'\s*RENPYTAG(\d+)END\s*', flags=re.IGNORECASE)

        def restore(match):
            try:
                idx = int(match.group(1))
                if 0 <= idx < len(original_tags):
                    return original_tags[idx]
                else:
                    thread_safe_print(f"⚠ Index de balise invalide: {idx} (max: {len(original_tags)-1})")
                    return ''
            except ValueError:
                thread_safe_print(f"⚠ Erreur de parsing d'index: {match.group(1)}")
                return ''

        restored = pattern_tag.sub(restore, translated)

        # Nettoyage final : supprime les balises orphelines restantes (même mal formatées)
        orphan_pattern = re.compile(r'\s*RENPYTAG\d+END\s*', flags=re.IGNORECASE)
        restored = orphan_pattern.sub('', restored)

        return restored

    def fix_quotes_universal(self, lines):
        """
        Convertit automatiquement les dialogues 'problématiques' en format compatible Ren'Py :
        - Convertit "Le mot \"prison\"." --> 'Le mot "prison".'
        - Échappe les apostrophes internes : 'l\'école'
        - Garde les balises {w}, {p}, etc. intactes
        """
        def replace_unescaped_quotes(s):
            s = re.sub(r'(?<!\\)\'', r"\\'", s)
            s = s.replace('\\"', '"')
            return s

        fixed = []
        pattern = re.compile(r'^(\s*\w*\s*)"(.*)"(\s*)$')
        for line in lines:
            match = pattern.match(line.rstrip('\n'))
            if match:
                prefix, content, suffix = match.groups()
                needs_fix = '\\"' in content or "'" in content
                if needs_fix:
                    safe_content = replace_unescaped_quotes(content)
                    fixed_line = f"{prefix}'{safe_content}'{suffix}\n"
                    fixed.append(fixed_line)
                else:
                    fixed.append(line)
            else:
                fixed.append(line)
        return fixed

    def translate_file(self, input_file: str, target_lang: str = 'fr'):
        """Traduit un fichier RPY individuel"""
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translated_lines = []
        translated_count = 0
        error_count = 0

        ignore_patterns = [
            r'^\s*#',                       # Commentaires
            r'^\s*$',                       # Lignes vides
            r'^\s*old\s+"',                 # Ligne old
            r'^\s*new\s+"old:.*"',          # new "old:xxxx"
            r'^\s*new\s*".*_\d+(\.\d+)*_?\d*"',  # new "xxx_1234" etc
            r'.*\.(webp|webm|mp4|mov|png|jpg|jpeg|gif|bmp|mp3|ogg|wav|mp4|mkv|avi|mov|flac|svg|ico|ttf|otf|eot|woff2?).*"',    # (optionnel) pour d'autres formats
        ]

        # Utilise une progress bar avec position différente pour chaque thread
        thread_id = threading.get_ident()
        desc = f"[Thread {thread_id % 1000}] {os.path.basename(input_file)}"
        
        for i, line in enumerate(tqdm(lines, desc=desc, position=thread_id % self.max_workers, leave=False)):
            if any(re.match(p, line) for p in ignore_patterns):
                translated_lines.append(line)
                continue

            # Trouve tous les textes entre guillemets
            matches = list(re.finditer(r'"((?:[^"\\]|\\.)*)"', line))
            if matches:
                new_line = line
                for match in matches:
                    original_text = match.group(1)

                    # Formate le texte avant la traduction
                    formatted_text = self.format_text(original_text)
                    
                    # Préserve les balises Ren'Py
                    clean_text, preserved_tags = self.preserve_renpy_tags(formatted_text)
                    
                    # Vérifie si il y a du texte à traduire après suppression des balises
                    text_to_check = re.sub(r'\s*RENPYTAG\d+END\s*', '', clean_text).strip()
                    
                    if not text_to_check:
                        # Pas de texte à traduire, on garde l'original
                        translated_text = original_text
                    else:
                        try:
                            # Traduit le texte nettoyé
                            translated_clean = self.translate_text(clean_text, target_lang)
                            
                            # Restaure les balises
                            translated_text = self.restore_renpy_tags(translated_clean, preserved_tags)

                            # Correction du texte traduit pour ajouter les espaces
                            translated_text = self.format_text(translated_text)
                            
                            # Nettoyage final des espaces multiples
                            translated_text = re.sub(r'\s+', ' ', translated_text).strip()
                            
                            # Échappe les guillemets internes pour Ren'Py
                            translated_text = translated_text.replace('"', '\\"')
                            
                            translated_count += 1
                            time.sleep(0.05)  # Réduit le délai pour LibreTranslate
                            
                        except Exception as e:
                            thread_safe_print(f"❌ Erreur ligne {i+1} dans {input_file}: {e}")
                            translated_text = original_text
                            error_count += 1
                    
                    # Remplace dans la ligne
                    new_line = new_line.replace(f'"{original_text}"', f'"{translated_text}"', 1)
                
                translated_lines.append(new_line)
            else:
                translated_lines.append(line)

        # Correction des guillemets/apostrophes
        translated_lines = self.fix_quotes_universal(translated_lines)

        # Écrit le fichier traduit
        with open(input_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)

        thread_safe_print(f"✓ {translated_count} lignes traduites – ⚠ {error_count} erreurs dans {os.path.basename(input_file)}")
        return translated_count, error_count

    def generate_language_files(self, game_path: str):
        files_content = {
            "change_language_entrance.rpy": '''init python early hide:
    import os
    global importlib
    global inspect
    import importlib
    import inspect
    global check_function_exists
    def check_function_exists(module_name, function_name):
        try:
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            if inspect.isfunction(function):
                return True
            else:
                return False
        except ImportError:
            return False
        except AttributeError:
            return False

    global my_old_show_screen
    my_old_show_screen = renpy.show_screen
    global my_old_lookup
    my_old_lookup = None
    if check_function_exists('renpy.ast.Translate','lookup'):
        my_old_lookup = renpy.ast.Translate.lookup
    def my_show_screen(_screen_name, *_args, **kwargs):
        if _screen_name == 'preferences':
            _screen_name = 'my_preferences'
        if _screen_name == 'director':
            if my_old_lookup is not None:
                renpy.ast.Translate.lookup = my_old_lookup
        return my_old_show_screen(_screen_name, *_args, **kwargs)
    renpy.show_screen = my_show_screen

screen my_preferences():
    python:
        global os
        import os
        def traverse_first_dir(path):
            translator = renpy.game.script.translator
            languages = translator.languages
            l = languages
            if (os.path.exists(path)):
                files = os.listdir(path)
                for file in files:
                    m = os.path.join(path,file)
                    if (os.path.isdir(m)):
                        h = os.path.split(m)
                        l.add(h[1])
            return l
        l = traverse_first_dir('game/tl')
    tag menu
    use preferences
    vbox:
        align(.98, .01)
        hbox:
            box_wrap True
            vbox:
                label _("Language")
                textbutton "Default" action Language(None)
                $ cnt = 0
                for i in l:
                    if i is not None and i != 'None':
                        textbutton "%s" % i action Language(i)
    ''',

            "set_default_language_at_startup.rpy": '''init 1000 python:
        renpy.game.preferences.language = "french"
    '''
        }
        for filename, content in files_content.items():
            filepath = os.path.join(game_path, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fichier généré : {filepath}")

    def translate_project_parallel(self, game_path: str = None, language: str = "french", target_lang: str = 'fr'):
        """Traduit un projet complet avec traitement parallèle des fichiers"""
        if game_path is None:
            game_path = self.find_game_folder()
        if not game_path:
            print("❌ Dossier 'game' introuvable! Assurez-vous d'être dans le répertoire du projet Ren'Py")
            return

        print(f"🎮 Projet Ren'Py détecté: {game_path}")
        translation_path = self.get_translation_path(game_path, language)

        if not os.path.exists(translation_path):
            print(f"❌ Dossier de traductions introuvable: {translation_path}")
            return

        backup_path = self.create_backup(translation_path)
        rpy_files = self.find_rpy_files(translation_path)

        if not rpy_files:
            print(f"❌ Aucun fichier .rpy trouvé dans {translation_path}")
            return

        print(f"📁 {len(rpy_files)} fichiers .rpy trouvés")
        print(f"🚀 Lancement de la traduction parallèle avec {self.max_workers} threads...")
        
        total_translated = 0
        total_errors = 0
        completed_files = 0

        # Traitement parallèle des fichiers
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Soumet tous les fichiers pour traduction
            future_to_file = {
                executor.submit(self.translate_file, rpy_file, target_lang): rpy_file 
                for rpy_file in rpy_files
            }
            
            # Collecte les résultats au fur et à mesure
            for future in as_completed(future_to_file):
                rpy_file = future_to_file[future]
                try:
                    translated, errors = future.result()
                    total_translated += translated
                    total_errors += errors
                    completed_files += 1
                    
                    thread_safe_print(f"📋 Progression: {completed_files}/{len(rpy_files)} fichiers traités")
                    
                except Exception as e:
                    thread_safe_print(f"❌ Erreur lors du traitement de {rpy_file}: {e}")
                    total_errors += 1
                    completed_files += 1

        self.generate_language_files(game_path)
        print(f"\n🎉 Traduction terminée : {total_translated} lignes traduites, {total_errors} erreurs.")
        print(f"💾 Une sauvegarde est disponible dans : {backup_path}")

    def translate_project(self, game_path: str = None, language: str = "french", target_lang: str = 'fr'):
        """Wrapper pour la compatibilité - utilise le traitement parallèle"""
        self.translate_project_parallel(game_path, language, target_lang)

def main():
    print("🎮 Auto-traducteur Ren'Py - Version Parallèle")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(description='Auto-traducteur automatique pour projets Ren\'Py')
    parser.add_argument('-p', '--path', help='Chemin vers le dossier game (détection automatique par défaut)')
    parser.add_argument('-l', '--lang', default='fr', help='Langue cible (par défaut: fr)')
    parser.add_argument('--translation-lang', default='french', help='Dossier de langue (par défaut: french)')
    parser.add_argument('-s', '--service', choices=['google', 'libretranslate'], 
                       default='google', help='Service de traduction (par défaut: google)')
    parser.add_argument('--libretranslate-url', default='http://localhost:5000',
                       help='URL LibreTranslate (par défaut: http://localhost:5000)')
    parser.add_argument('-f', '--file', help='Traduire un fichier spécifique au lieu du projet complet')
    parser.add_argument('--files', nargs='+', help='Traduire plusieurs fichiers RPY dans le dossier de langue')
    parser.add_argument('--max-workers', type=int, default=3, 
                       help='Nombre max de fichiers traités en parallèle (par défaut: 3)')
    
    args = parser.parse_args()
    
    # Limite le nombre de workers pour éviter la surcharge
    max_workers = min(args.max_workers, 5)  # Max 5 threads
    
    translator = RenpyAutoTranslator(
        service=args.service,
        libretranslate_url=args.libretranslate_url,
        max_workers=max_workers
    )
    
    print(f"⚙️ Configuration: {args.service} avec {max_workers} thread(s) parallèle(s)")
    
    # Mode fichier unique
    if args.file:
        if os.path.exists(args.file):
            print(f"📝 Traduction du fichier: {args.file}")
            translated, errors = translator.translate_file(args.file, args.lang)
            print(f"✅ Terminé: {translated} lignes traduites, {errors} erreurs")
        else:
            print(f"❌ Fichier introuvable: {args.file}")
        return

    # Mode multi-fichiers dans le dossier langue (avec parallélisation)
    if args.files:
        game_path = args.path if args.path else translator.find_game_folder()
        if not game_path:
            print("❌ Dossier 'game' introuvable")
            return

        translation_path = translator.get_translation_path(game_path, args.translation_lang)
        
        # Créer la liste des fichiers complets
        file_paths = []
        for filename in args.files:
            file_path = os.path.join(translation_path, filename)
            if os.path.exists(file_path):
                file_paths.append(file_path)
            else:
                print(f"❌ Fichier introuvable : {file_path}")
        
        if file_paths:
            print(f"🚀 Traduction parallèle de {len(file_paths)} fichiers...")
            total_translated = 0
            total_errors = 0
            
            # Traitement parallèle des fichiers spécifiés
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(translator.translate_file, file_path, args.lang): file_path 
                    for file_path in file_paths
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        translated, errors = future.result()
                        total_translated += translated
                        total_errors += errors
                    except Exception as e:
                        print(f"❌ Erreur lors du traitement de {file_path}: {e}")
                        total_errors += 1
            
            print(f"✅ Terminé: {total_translated} lignes traduites, {total_errors} erreurs au total")
        return
    
    # Mode projet complet avec parallélisation
    translator.translate_project(
        game_path=args.path,
        language=args.translation_lang,
        target_lang=args.lang
    )

if __name__ == "__main__":
    main()