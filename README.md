# Auto Renpy Translator

An automatic translation tool for Ren'Py projects that translates all generated translation files automatically.

## 📋 Requirements

- Python 3.6 or later
- A Ren'Py project with extracted translation files
- Internet connection (for Google Translate) or local LibreTranslate

## 🚀 Installation and Usage

### Step 1: Extract Translation Files

Before using this tool, you must first extract translation files from your Ren'Py project:

1. Download and use **renpy-translator**:
   ```bash
   git clone https://github.com/anonymousException/renpy-translator
   ```

2. Follow the instructions of the renpy-translator project to extract `.rpy` files into the `game/tl/[language]/` folder.

### Step 2: Use the Auto Translator

1. **Clone this project** into your Ren'Py game directory:
   ```bash
   git clone https://github.com/your-username/auto-renpy-translator
   ```

2. **Place the files** into the root of your Ren'Py project:
   ```
   MyRenpyGame/
   ├── game/
   │   ├── tl/
   │   │   └── french/  # .rpy files extracted by renpy-translator
   │   └── ...
   ├── AutoRenpyTranslator.py
   └── AutoRenpyTranslator.bat
   ```

3. **Run the translator**:

   **On Windows:**
   ```bash
   AutoRenpyTranslator.bat
   ```

   **On Linux/Mac:**
   ```bash
   python AutoRenpyTranslator.py
   ```

## ⚙️ Advanced Options

### CLI Usage

```bash
# Automatic translation (Google Translate)
python AutoRenpyTranslator.py

# Using local LibreTranslate
python AutoRenpyTranslator.py --service libretranslate

# Specify a custom path
python AutoRenpyTranslator.py --path /path/to/game

# Translate to another language
python AutoRenpyTranslator.py --lang es --translation-lang spanish

# Translate a specific file
python AutoRenpyTranslator.py --file game/tl/french/script.rpy
```

### Available Parameters

- `--path`: Path to the `game` folder (auto-detected by default)
- `--lang`: Target language code (default: `fr`)
- `--translation-lang`: Name of the language folder (default: `french`)
- `--service`: Translation service (`google` or `libretranslate`)
- `--libretranslate-url`: LibreTranslate URL (default: `http://localhost:5000`)
- `--file`: Translate a specific file

## 🔧 Translation Services

### Google Translate (default)
- **Pros**: Free, no setup required
- **Cons**: Limited to 5000 characters per request, may get rate-limited

### LibreTranslate
- **Pros**: Unlimited, private, fast
- **Cons**: Requires local installation

#### Install LibreTranslate

```bash
# Using pip
pip install libretranslate

# Start the server
libretranslate --host 0.0.0.0 --port 5000

# Then use the translator
python AutoRenpyTranslator.py --service libretranslate
```

## 📁 Project Structure

```
MyRenpyGame/
├── game/
│   ├── tl/
│   │   └── french/           # .rpy files to translate
│   │       ├── script.rpy
│   │       ├── characters.rpy
│   │       └── ...
│   ├── change_language_entrance.rpy    # Auto-generated
│   ├── set_default_language_at_startup.rpy  # Auto-generated
│   └── ...
├── backup_translations_YYYYMMDD_HHMMSS/  # Auto backup
├── AutoRenpyTranslator.py
└── AutoRenpyTranslator.bat
```

## 🛡️ Safety

- **Auto-backup**: A backup is created before each translation
- **Tag preservation**: Ren'Py tags (`{b}`, `{i}`, `{w}`, etc.) are preserved
- **Error handling**: Errors do not stop the process

## 🌐 Supported Languages

The script supports all languages available in Google Translate. Examples:

- `fr`: French
- `es`: Spanish
- `de`: German
- `it`: Italian
- `pt`: Portuguese
- `ru`: Russian
- `ja`: Japanese
- `ko`: Korean
- `zh`: Chinese

## 🔍 Features

- ✅ **Auto-detection** of the `game` folder
- ✅ **Smart translation** that preserves Ren'Py tags
- ✅ **Automatic backup** before translation
- ✅ **Robust error handling**
- ✅ **Large file support** (auto chunking)
- ✅ **Auto dependency installation**
- ✅ **Automatic generation** of language config files
- ✅ **Progress bar** to track progress

## 🐛 Troubleshooting

### Common Issues

**"Game folder not found" error**
- Ensure you're in the correct directory
- Use `--path` to manually specify the folder

**Google Translate error**
- Check your internet connection
- Wait a few minutes (rate-limiting)
- Try LibreTranslate: `--service libretranslate`

**LibreTranslate error**
- Check that LibreTranslate is installed and running
- Test the URL: `curl http://localhost:5000/languages`

## 📝 Full Workflow

1. **Prepare your Ren'Py project** with source files
2. **Extract translations** with [renpy-translator](https://github.com/anonymousException/renpy-translator)
3. **Clone this tool** into your project folder
4. **Run the translation** with `AutoRenpyTranslator.bat`
5. **Test the game** with the new translations
6. **Tweak if needed** and re-run

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Add new features
- Improve the documentation

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more info.

## 🙏 Thanks

- [renpy-translator](https://github.com/anonymousException/renpy-translator) for extracting files
- [googletrans](https://github.com/ssut/googletrans) for the Google Translate API
- [LibreTranslate](https://github.com/LibreTranslate/LibreTranslate) for the free alternative