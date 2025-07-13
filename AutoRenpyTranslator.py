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

    def get_translation_path(self, game_path: str, language: str) -> str:
        """Obtient le chemin du dossier de traductions"""
        return os.path.join(game_path, 'tl', language)

    def find_rpy_files(self, path: str) -> List[str]:
        """Trouve tous les fichiers .rpy dans un dossier"""
        rpy_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.rpy'):
                    rpy_files.append(os.path.join(root, file))
        return rpy_files

    def translate_text(self, text: str, target_lang: str) -> str:
        """Traduit un texte avec le service sélectionné"""
        if not text or not text.strip():
            return text
            
        if self.service == 'google':
            return self._translate_google(text, target_lang)
        elif self.service == 'libretranslate':
            return self._translate_libretranslate(text, target_lang)
        else:
            raise ValueError(f"Service de traduction non supporté: {self.service}")

    def _translate_google(self, text: str, target_lang: str) -> str:
        """Traduit avec Google Translate"""
        if not self.google_translator:
            raise Exception("Google Translator non initialisé")
            
        # Diviser le texte si trop long
        if len(text) > self.google_char_limit:
            return self._translate_long_text(text, target_lang)
            
        try:
            result = self.google_translator.translate(text, dest=target_lang)
            return result.text
        except Exception as e:
            print(f"Erreur Google Translate: {e}")
            return text

    def _translate_libretranslate(self, text: str, target_lang: str) -> str:
        """Traduit avec LibreTranslate"""
        try:
            response = requests.post(
                f"{self.libretranslate_url}/translate",
                json={
                    "q": text,
                    "source": "auto",
                    "target": target_lang,
                    "format": "text"
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()['translatedText']
            else:
                print(f"Erreur LibreTranslate: {response.status_code}")
                return text
        except Exception as e:
            print(f"Erreur LibreTranslate: {e}")
            return text

    def _translate_long_text(self, text: str, target_lang: str) -> str:
        """Traduit les textes longs en préservant la structure des paragraphes"""
        # Diviser par paragraphes doubles
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                try:
                    translated_para = self.translate_text(paragraph.strip(), target_lang)
                    translated_paragraphs.append(translated_para)
                    time.sleep(0.1)  # Pause entre paragraphes
                except Exception as e:
                    print(f"❌ Erreur traduction paragraphe: {e}")
                    translated_paragraphs.append(paragraph)
            else:
                translated_paragraphs.append(paragraph)
        
        return '\n\n'.join(translated_paragraphs)

    def preserve_renpy_tags(self, text: str) -> Tuple[str, List]:
        """Préserve les balises Ren'Py et retourne le texte nettoyé + segments"""
        if not text:
            return text, []
        
        segments = []
        clean_text = ""
        last_end = 0
        
        # Pattern pour les balises Ren'Py {tag}, [tag], \\n, etc.
        pattern = r'(\{[^}]*\}|\[[^\]]*\]|\\n|\\t)'
        
        for match in re.finditer(pattern, text):
            start, end = match.span()
            tag = match.group(1)
            
            # Ajouter le texte avant la balise
            if start > last_end:
                part = text[last_end:start]
                clean_text += part
                segments.append(('text', part, part))
            
            # Ajouter la balise
            if tag == '\\n':
                segments.append(('newline', tag, tag))
            else:
                segments.append(('tag', tag, tag))
            
            last_end = end
        
        # Ajouter le reste du texte après la dernière balise
        if last_end < len(text):
            part = text[last_end:]
            clean_text += part
            segments.append(('text', part, part))
        
        return clean_text, segments

    def restore_renpy_tags(self, translated_text: str, original_text: str) -> str:
        """Restaure les balises Ren'Py dans le texte traduit en respectant la structure"""
        clean_original, original_segments = self.preserve_renpy_tags(original_text)

        if not original_segments:
            return translated_text

        # Cas spécial pour les longs textes : si le texte original contient \n\n, 
        # on divise par paragraphes
        if '\\n\\n' in original_text:
            return self._restore_with_paragraphs(translated_text, original_text, original_segments)

        # Méthode standard pour textes courts
        # On appelle _restore_standard et on lui donne 'original_text' comme 3ème argument
        return self._restore_standard(translated_text, original_segments, original_text)

    def _restore_with_paragraphs(self, translated_text: str, original_text: str, original_segments: List) -> str:
        """Restaure les balises pour les textes longs avec paragraphes"""
        # Diviser le texte original en paragraphes
        original_paragraphs = original_text.split('\\n\\n')
        translated_paragraphs = translated_text.split('\n\n')
        
        # Si le nombre de paragraphes ne correspond pas, utiliser la méthode standard
        if len(original_paragraphs) != len(translated_paragraphs):
            return self._restore_standard(translated_text, original_segments, original_text)  # ✅ Ajout du 3ème paramètre
        
        # Restaurer chaque paragraphe individuellement
        restored_paragraphs = []
        for orig_para, trans_para in zip(original_paragraphs, translated_paragraphs):
            # Nettoyer les balises du paragraphe original
            clean_orig, para_segments = self.preserve_renpy_tags(orig_para)
            
            if clean_orig.strip():
                # ✅ Correction : ajouter le 3ème paramètre 'orig_para'
                restored_para = self._restore_standard(trans_para, para_segments, orig_para)
                restored_paragraphs.append(restored_para)
            else:
                restored_paragraphs.append(trans_para)
        
        return '\\n\\n'.join(restored_paragraphs)

    def _restore_standard(self, translated_text: str, original_segments: List, original_full_text: str) -> str:
        """Méthode standard de restauration des balises"""
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
            elif segment_type == 'newline':
                result_parts.append('\\n')
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

                    segment_text = translated_text[translated_pos:end_pos]
                    translated_pos = end_pos

                    result_parts.append(segment_text)
                else:
                    result_parts.append('')

        final_text = ''.join(result_parts)
        return self.fix_w_position(final_text, original_full_text)

    def fix_w_position(self, translated_text: str, original_text: str) -> str:
        """Corrige la position des balises {w} dans le texte traduit"""
        # Supprimer les balises {w} pour éviter les bugs
        return re.sub(r'\{w\}', '', translated_text)

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

                    # --- Début de la zone à modifier ---
                    # Capturer le préfixe (indentation et 'new "') et le suffixe ('"\n' ou autre)
                    prefix = line[:match.start(1)-1] # Capture jusqu'au guillemet ouvrant
                    suffix = line[match.end(1)+1:]   # Capture à partir du guillemet fermant + 1

                    # Éviter de traduire les textes vides ou très courts
                    if len(original.strip()) < 3:
                        translated_lines.append(line)
                        continue

                    try:
                        clean_text, _ = self.preserve_renpy_tags(original)

                        # Pour les très longs textes, diviser en sections
                        if len(clean_text) > 1000:
                            translated_clean = self._translate_long_text(clean_text, target_lang)
                        else:
                            translated_clean = self.translate_text(clean_text, target_lang)

                        translated_text = self.restore_renpy_tags(translated_clean, original)

                        # Échapper les guillemets standard et potentiellement d'autres caractères problématiques
                        # Si tu identifies d'autres caractères (comme “ ou ”) qui cassent,
                        # tu peux ajouter d'autres .replace() ici.
                        escaped_translated_text = translated_text.replace('"', '\\"')
                        # Exemple si les guillemets typographiques cassent :
                        # escaped_translated_text = escaped_translated_text.replace('“', '\\"').replace('”', '\\"')


                        # Reconstruire la ligne manuellement
                        translated_line = f'{prefix}"{escaped_translated_text}"{suffix}'

                        # --- Fin de la zone à modifier ---

                        translated_lines.append(translated_line)
                        translated_count += 1
                        time.sleep(0.1) # Garder une petite pause entre les requêtes

                    except Exception as e:
                        print(f"❌ Erreur à la ligne {i}: {e}")
                        translated_lines.append(line) # Ajouter la ligne originale en cas d'erreur
                        error_count += 1
                else:
                    # Si le regex initial matche "new " mais qu'il n'y a pas de texte entre guillemets (rare)
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
