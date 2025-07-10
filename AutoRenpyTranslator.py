#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import argparse
import os
import shutil
from datetime import datetime
from typing import List, Tuple, Optional
import subprocess
import sys


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
    
    # Installer requests
    requests = install_and_import('requests')
    tqdm      = install_and_import('tqdm') 
    
    # Installer googletrans
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

# Importation avec installation automatique
requests, Translator = safe_import()

class RenpyAutoTranslator:
    def __init__(self, service='google', libretranslate_url='http://localhost:5000'):
        self.service = service
        self.libretranslate_url = libretranslate_url
        self.google_translator = None
        
        if service == 'google':
            try:
                self.google_translator = Translator()
                # Test de connexion
                self.google_translator.translate("test", dest='fr')
                print("✓ Google Translate connecté")
            except Exception as e:
                print(f"⚠ Problème avec Google Translate: {e}")
                print("Passage en mode LibreTranslate recommandé")
        
        # Limites de caractères pour Google Translate
        self.google_char_limit = 5000
        
    def create_backup(self, source_path: str) -> str:
        """Crée une sauvegarde du dossier de traductions"""
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
        """Trouve le dossier 'game' dans le projet Ren'Py"""
        # Chercher dans le répertoire courant
        game_path = os.path.join(start_path, "game")
        if os.path.exists(game_path):
            return game_path
        
        # Chercher dans les sous-dossiers
        for root, dirs, files in os.walk(start_path):
            if "game" in dirs:
                return os.path.join(root, "game")
        
        return None
    

    def get_translation_path(self, game_path: str, language: str = "french") -> str:
        """Obtient le chemin du dossier de traductions"""
        return os.path.join(game_path, "tl", language)
    
    def find_rpy_files(self, path: str) -> List[str]:
        """Trouve tous les fichiers .rpy dans un dossier et ses sous-dossiers"""
        rpy_files = []
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.rpy'):
                        rpy_files.append(os.path.join(root, file))
        return rpy_files
    
    def translate_text(self, text: str, target_lang: str = 'fr', source_lang: str = 'en') -> str:
        """Traduit un texte selon le service choisi"""
        if not text.strip():
            return text
            
        try:
            if self.service == 'google':
                return self._translate_google(text, target_lang, source_lang)
            elif self.service == 'libretranslate':
                return self._translate_libretranslate(text, target_lang, source_lang)
        except Exception as e:
            print(f"❌ Erreur de traduction: {e}")
            return text
    
    def _translate_google(self, text: str, target_lang: str, source_lang: str) -> str:
        """Traduction avec Google Translate (gratuit)"""
        if not self.google_translator:
            raise Exception("Google Translator non initialisé")
            
        # Gestion de la limite de caractères
        if len(text) > self.google_char_limit:
            chunks = self._split_text(text, self.google_char_limit)
            translated_chunks = []
            
            for chunk in chunks:
                if chunk.strip():
                    try:
                        result = self.google_translator.translate(chunk, dest=target_lang, src=source_lang)
                        translated_chunks.append(result.text)
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"❌ Erreur chunk: {e}")
                        translated_chunks.append(chunk)
                else:
                    translated_chunks.append(chunk)
            
            return ''.join(translated_chunks)
        else:
            result = self.google_translator.translate(text, dest=target_lang, src=source_lang)
            return result.text
    
    def _translate_libretranslate(self, text: str, target_lang: str, source_lang: str) -> str:
        """Traduction avec LibreTranslate local"""
        data = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        try:
            response = requests.post(f"{self.libretranslate_url}/translate", data=data, timeout=10)
            if response.status_code == 200:
                return response.json()['translatedText']
            else:
                raise Exception(f"Erreur LibreTranslate: {response.status_code}")
        except requests.exceptions.ConnectionError:
            raise Exception("Impossible de se connecter à LibreTranslate. Vérifiez qu'il est lancé.")
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Divise le texte en chunks respectant la limite de caractères"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        sentences = re.split(r'([.!?]\s+)', text)
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                else:
                    words = sentence.split()
                    word_chunk = ""
                    for word in words:
                        if len(word_chunk + " " + word) <= max_length:
                            word_chunk += " " + word if word_chunk else word
                        else:
                            if word_chunk:
                                chunks.append(word_chunk)
                            word_chunk = word
                    if word_chunk:
                        current_chunk = word_chunk
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def extract_translatable_text(self, line: str) -> Optional[str]:
        """Extrait le texte à traduire d'une ligne Ren'Py"""
        # Ligne de dialogue avec caractère
        match = re.search(r'^\s*(\w+)\s+"((?:[^"\\]|\\.)*)"', line)
        if match:
            return match.group(2)
        
        # Ligne de narration
        match = re.search(r'^\s*"((?:[^"\\]|\\.)*)"', line)
        if match:
            return match.group(1)
        
        # Ligne new dans strings
        match = re.search(r'^\s*new\s+"([^"]*)"', line)
        if match:
            return match.group(1)
        
        return None
    
    def preserve_renpy_tags(self, text: str) -> Tuple[str, List[Tuple[str, str, str]]]:
        """Extrait les balises Ren'Py et retourne le texte nettoyé avec les segments"""
        # Diviser le texte en segments : [texte_avant, balise, texte_après, balise, ...]
        tag_pattern = r'(\{[^}]*\})'
        parts = re.split(tag_pattern, text)
        
        clean_text = ""
        segments = []
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Texte normal
                clean_text += part
                segments.append(('text', part, part))
            else:  # Balise
                segments.append(('tag', part, ''))
        
        return clean_text, segments

    @staticmethod
    def protect_renpy_variables(text):
        """Remplace les balises et variables Ren'Py par des jetons temporaires"""
        tokens = []
        def replacer(match):
            tokens.append(match.group(0))
            return f"__TOKEN_{len(tokens)-1}__"

        # Match des balises {b}, {/b}, [var], etc.
        protected_text = re.sub(r'(\{[^}]+\}|\[[^\]]+\])', replacer, text)
        return protected_text, tokens

    @staticmethod
    def restore_renpy_variables(text, tokens):
        for i, token in enumerate(tokens):
            text = text.replace(f"__TOKEN_{i}__", token)
        return text


    def fix_w_position(self, translated_text: str, original_text: str) -> str:
        # Vérifier si {w} est présent dans le texte original
        # supprimer pour cause de bug

        # # Cas 1 : déplacer ponctuation avant {w} (ex : "Bonjour{w} !" → "Bonjour!{w}")
        # pattern1 = re.compile(r'\{w\}(\s*)([,.!?:;])')
        
        # def replacer1(m):
        #     espaces = m.group(1)
        #     ponctuation = m.group(2)
        #     return ponctuation + '{w}' + espaces

        # text = pattern1.sub(replacer1, translated_text)

        # # Cas 2 : déplacer {w} après la ponctuation si {w} est collé au mot et ponctuation suit (ex : "jour{w}," → "jour,{w}")
        # pattern2 = re.compile(r'(\w)\{w\}([,.!?:;])')
        
        # def replacer2(m):
        #     lettre = m.group(1)
        #     ponctuation = m.group(2)
        #     return lettre + ponctuation + '{w}'

        # text = pattern2.sub(replacer2, text)

        # return text
        return re.sub(r'\{w\}', '', translated_text)


    def restore_renpy_tags(self, translated_text: str, original_text: str) -> str:
        """Restaure les balises Ren'Py dans le texte traduit en respectant la structure"""
        clean_original, original_segments = self.preserve_renpy_tags(original_text)

        if not original_segments:
            return translated_text

        # Extraire seulement les parties texte de l'original
        original_text_parts = [seg[1] for seg in original_segments if seg[0] == 'text']
        original_clean = ''.join(original_text_parts)

        if not original_clean.strip():
            return translated_text

        # Diviser le texte traduit proportionnellement
        result_parts = []
        translated_pos = 0

        for segment_type, content, _ in original_segments:
            if segment_type == 'tag':
                result_parts.append(content)
            else:  # segment_type == 'text'
                if not content:
                    result_parts.append('')
                    continue

                segment_length = len(content)
                original_total = len(original_clean)

                if original_total > 0:
                    proportion = segment_length / original_total
                    translated_segment_length = int(proportion * len(translated_text))

                    end_pos = min(translated_pos + translated_segment_length, len(translated_text))

                    # Ne pas couper un mot
                    while end_pos < len(translated_text) and translated_text[end_pos] not in ' \t\n.,!?;:':
                        end_pos += 1

                    # Étendre end_pos pour inclure {w} + ponctuation si présents juste après
                    while True:
                        if end_pos + 3 <= len(translated_text) and translated_text[end_pos:end_pos+3] == '{w}':
                            # vérifier s'il y a une ponctuation juste après {w}
                            if end_pos + 4 < len(translated_text) and translated_text[end_pos + 3] in '.,!?;:':
                                end_pos += 4  # inclure {w} + ponctuation
                                continue
                            else:
                                end_pos += 3  # inclure seulement {w}
                                continue
                        break

                    segment_text = translated_text[translated_pos:end_pos]
                    translated_pos = end_pos

                    result_parts.append(segment_text)
                else:
                    result_parts.append('')

        final_text = ''.join(result_parts)
        return self.fix_w_position(final_text, original_text)



    def generate_language_files(self, game_path: str):
        """Génère les fichiers de configuration de langue dans le dossier game/"""

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


    
    def translate_file(self, input_file: str, target_lang: str = 'fr') -> Tuple[int, int]:
        """Traduit un fichier Ren'Py et retourne (lignes_traduites, erreurs)"""
        if not os.path.exists(input_file):
            print(f"❌ Fichier introuvable: {input_file}")
            return 0, 1

        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        translated_lines = []
        translated_count = 0
        error_count = 0

        from tqdm import tqdm

        for i, line in enumerate(tqdm(lines,
                                desc=os.path.basename(input_file),
                                unit='ligne',
                                ncols=80), 1):

            stripped = line.strip()

            # Cas à ignorer
            if (
                stripped.startswith('#') or
                not stripped or
                ('translate french' in line and stripped.endswith(':')) or
                'TODO' in line or
                re.match(r'^\s*old\s+"', line)
            ):
                translated_lines.append(line)
                continue

            # Cas spécial new: "new:123.456_0" → ne pas traduire
            if re.match(r'^\s*new\s+"((new|old):\d+(\.\d+)?_\d+)"', line):
                translated_lines.append(line)
                continue

            # Cas: new "Texte"
            if re.match(r'^\s*new\s+"', line):
                match = re.search(r'^\s*new\s+"((?:[^"\\]|\\.)*)"', line)
                if match:
                    original = match.group(1)
                    try:
                        clean_text, _ = self.preserve_renpy_tags(original)
                        translated_clean = self.translate_text(clean_text, target_lang)
                        translated_text = self.restore_renpy_tags(translated_clean, original)
                        translated_text = translated_text.replace('"', '\\"')
                        translated_line = re.sub(r'(^\s*new\s+)"((?:[^"\\]|\\.)*)"', rf'\1"{translated_text}"', line)
                        translated_lines.append(translated_line)
                        translated_count += 1
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"❌ Erreur à la ligne {i}: {e}")
                        translated_lines.append(line)
                        error_count += 1
                else:
                    translated_lines.append(line)
                continue

            # Cas général : traduire tous les "..." trouvés sur la ligne (ex : "Author" "Text")
            matches = list(re.finditer(r'"((?:[^"\\]|\\.)*)"', line))
            if matches:
                new_line = line
                for match in matches:
                    original = match.group(1)
                    try:
                        clean_text, _ = self.preserve_renpy_tags(original)
                        translated_clean = self.translate_text(clean_text, target_lang)
                        translated_text = self.restore_renpy_tags(translated_clean, original)
                        translated_text = translated_text.replace('"', '\\"')
                        # Remplacer un seul groupe à la fois
                        new_line = new_line.replace(f'"{original}"', f'"{translated_text}"', 1)
                        translated_count += 1
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"❌ Erreur à la ligne {i}: {e}")
                        error_count += 1
                translated_lines.append(new_line)
            else:
                translated_lines.append(line)

        with open(input_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)

        print(f"✓ {translated_count} lignes traduites – ⚠ {error_count} erreurs")
        return translated_count, error_count


    
    def translate_project(self, game_path: str = None, language: str = "french", target_lang: str = 'fr'):
        """Traduit automatiquement tous les fichiers de traduction d'un projet Ren'Py"""
        
        # Trouver le dossier game automatiquement s'il n'est pas fourni
        if game_path is None:
            game_path = self.find_game_folder()
        
        if not game_path:
            print("❌ Dossier 'game' introuvable! Assurez-vous d'être dans le répertoire du projet Ren'Py")
            return
        
        print(f"🎮 Projet Ren'Py détecté: {game_path}")
        
        # Obtenir le chemin du dossier de traductions (ex : game/tl/french)
        translation_path = self.get_translation_path(game_path, language)
        
        if not os.path.exists(translation_path):
            print(f"❌ Dossier de traductions introuvable: {translation_path}")
            print("Assurez-vous que les fichiers de traduction existent dans ce dossier")
            return
        
        # Créer une sauvegarde automatique
        backup_path = self.create_backup(translation_path)
        
        # Trouver tous les fichiers .rpy dans ce dossier
        rpy_files = self.find_rpy_files(translation_path)
        
        if not rpy_files:
            print(f"❌ Aucun fichier .rpy trouvé dans {translation_path}")
            return
        
        print(f"📁 {len(rpy_files)} fichiers .rpy trouvés, lancement de la traduction...")
        
        total_translated = 0
        total_errors = 0
        
        for rpy_file in rpy_files:
            translated, errors = self.translate_file(rpy_file, target_lang=target_lang)
            total_translated += translated
            total_errors += errors
        
        # Générer les fichiers de langue dans game/
        self.generate_language_files(game_path)

        print(f"🎉 Traduction terminée : {total_translated} lignes traduites, {total_errors} erreurs.")
        print(f"💾 Une sauvegarde est disponible dans : {backup_path}")


def main():
    print("🎮 Auto-traducteur Ren'Py - Version Projet")
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
    
    args = parser.parse_args()
    
    # Créer le traducteur
    translator = RenpyAutoTranslator(
        service=args.service,
        libretranslate_url=args.libretranslate_url
    )
    
    # Mode fichier unique
    if args.file:
        if os.path.exists(args.file):
            print(f"📝 Traduction du fichier: {args.file}")
            translated, errors = translator.translate_file(args.file, args.lang)
            print(f"✅ Terminé: {translated} lignes traduites, {errors} erreurs")
        else:
            print(f"❌ Fichier introuvable: {args.file}")
        return
    
    # Mode projet complet
    translator.translate_project(
        game_path=args.path,
        language=args.translation_lang,
        target_lang=args.lang
    )

if __name__ == "__main__":
    main()