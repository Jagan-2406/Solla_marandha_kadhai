# 🏗️ Solla Marantha Kadhai — Full Project Architecture

> A Tamil NLP sentence generator and learning platform built with Flask + vanilla HTML/JS.

---

## 📁 Project Folder Structure

```
Solla Marantha Kadhai/           ← Root
│
├── backend/                     ← Python server (everything that runs on the server)
│   ├── app.py                   ← 🚀 ENTRY POINT — Flask web server
│   ├── grammar_engine.py        ← Tamil grammar logic (rule-based NLP engine)
│   ├── db_manager.py            ← Database helper (SQLite read/write functions)
│   ├── init_db.py               ← One-time script to set up the database
│   ├── tamil_nlp.db             ← SQLite database (vocabulary + grammar rules + saved sentences)
│   ├── .env                     ← Secret API keys (Gemini / Anthropic)
│   └── requirements.txt         ← Python package dependencies
│
└── frontend/                    ← All UI files (HTML, CSS, JS)
    ├── templates/               ← HTML pages (served by Flask)
    │   ├── index.html           ← Home page (Sentence Generator)
    │   ├── vocabulary.html      ← Vocabulary browser page
    │   ├── saved.html           ← Saved sentences page
    │   └── chatbot.html         ← AI Tutor chat page
    └── static/                  ← Static assets (served directly by Flask)
        ├── css/style.css        ← All styling (dark mode, animations, layout)
        ├── js/main.js           ← All frontend JavaScript logic
        ├── manifest.json        ← PWA manifest (makes it installable on mobile)
        ├── sw.js                ← Service Worker (offline caching)
        └── icon-192/512.png     ← App icons
```

---

## 🚀 Startup Sequence — What Runs First?

When you run `python app.py`, here's the exact order of execution:

```
1. app.py starts
   │
   ├── 2. Loads .env file → reads GEMINI_API_KEY and ANTHROPIC_API_KEY
   │
   ├── 3. Tries to connect to Gemini AI (google-genai SDK)
   │       → If GEMINI_API_KEY starts with 'AIzaSy' → Gemini is enabled ✅
   │       → Otherwise falls back to Anthropic Claude
   │       → If neither works → uses built-in fallback responses
   │
   ├── 4. Creates the Flask app object
   │       → Points template_folder to ../frontend/templates
   │       → Points static_folder to ../frontend/static
   │
   ├── 5. Imports & initializes TamilGrammarEngine from grammar_engine.py
   │       → grammar_engine.py internally calls db_manager.py to load
   │         subject pronouns (நான், அவன், அவள், etc.) from the database
   │
   └── 6. Flask starts listening on http://127.0.0.1:5000 🟢
```

---

## 🌐 How the Browser Gets the Pages

```
Browser visits http://127.0.0.1:5000
       │
       ▼
   app.py  →  @app.route('/')  →  render_template('index.html')
                                         │
                                         ▼
                              frontend/templates/index.html
                                         │
                              (inside index.html, it loads):
                                ├── /static/css/style.css
                                └── /static/js/main.js
```

Flask serves HTML from `frontend/templates/` and static files (CSS/JS/images) from `frontend/static/`. **The browser never directly touches the backend files** — everything goes through Flask routes.

---

## 🔗 Complete File Relationship Map

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER (User's Screen)               │
│                                                         │
│  index.html ──loads──► style.css  (all visual styling) │
│       │         └────► main.js    (all interactivity)   │
│       │                                                 │
│       │  User clicks "Generate" button                  │
│       │  → main.js calls fetch("/generate", {...})      │
│       │                    │                            │
└───────────────────────────┼────────────────────────────┘
                            │  HTTP POST (JSON data)
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   BACKEND (Flask Server)                 │
│                                                         │
│  app.py  ◄── receives the request                       │
│    │                                                    │
│    ├── @route('/generate')                              │
│    │       └──► grammar_engine.py                       │
│    │               └──► db_manager.py (get subjects)    │
│    │                       └──► tamil_nlp.db (SQLite)   │
│    │                                                    │
│    ├── @route('/tts')                                   │
│    │       └──► gTTS library (Google TTS API online)    │
│    │               └── returns MP3 audio bytes          │
│    │                                                    │
│    ├── @route('/save')                                  │
│    │       └──► db_manager.py → tamil_nlp.db            │
│    │                                                    │
│    ├── @route('/variations')                            │
│    │       └──► Gemini AI API (or Anthropic / fallback) │
│    │                                                    │
│    └── @route('/chat')                                  │
│            └──► Gemini AI API (or Anthropic / fallback) │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints (What Each URL Does)

| HTTP Method | URL | Called By | What Happens |
|---|---|---|---|
| `GET` | `/` | Browser navigation | Returns `index.html` (Home page) |
| `GET` | `/vocabulary` | Nav link click | Returns `vocabulary.html` |
| `GET` | `/saved` | Nav link click | Returns `saved.html` |
| `GET` | `/chatbot` | Nav link click | Returns `chatbot.html` |
| `POST` | `/generate` | `main.js → generateSentence()` | Calls `grammar_engine.py` → returns Tamil sentence JSON |
| `POST` | `/tts` | `main.js → speakText()` | Calls gTTS → returns MP3 audio |
| `POST` | `/save` | `main.js → saveSentence()` | Calls `db_manager.py → save_sentence()` → saves to DB |
| `GET` | `/api/saved` | `saved.html` page JS | Calls `db_manager.py → get_saved()` → returns list |
| `DELETE` | `/api/saved/<id>` | `saved.html` delete button | Calls `db_manager.py → delete_saved()` |
| `GET` | `/api/vocabulary` | `vocabulary.html` page JS | Calls `db_manager.py → get_all_vocabulary()` |
| `POST` | `/variations` | `main.js → getVariations()` | Calls Gemini/Anthropic AI API → returns 3 alternatives |
| `POST` | `/chat` | `chatbot.html` page JS | Calls Gemini/Anthropic AI → returns tutor reply |

---

## 🧠 How Each Backend File Works

### `app.py` — The Brain / Traffic Controller
- **Starts** the Flask web server
- **Registers** all URL routes (like a menu of what the server can do)
- **Delegates** work to other files:
  - Grammar → `grammar_engine.py`
  - Database → `db_manager.py`
  - Text-to-Speech → `gTTS` library
  - AI replies → Gemini or Anthropic

### `grammar_engine.py` — The Tamil Language Expert
- Contains `SUPPORTED_VERBS` dictionary with pre-defined conjugation stems for 10 Tamil verbs
- `TamilGrammarEngine` class has 3 main methods:
  - `generate_statement()` → "நான் பால் குடிக்கிறேன்"
  - `generate_question()` → "நான் பால் குடிக்கிறேனா?"
  - `generate_dialogue()` → Returns a list of 2 speaker lines (Friend asks, Subject replies)
- If a verb isn't in `SUPPORTED_VERBS`, it uses **heuristic fallback rules** to guess conjugation

### `db_manager.py` — The Database Librarian
- Opens `tamil_nlp.db` (SQLite file) for every query, then closes it
- Functions:
  - `get_all_vocabulary()` → reads `vocabulary` table
  - `search_vocabulary(q)` → searches vocabulary by Tamil word or English meaning
  - `get_suffix(tense, gender)` → reads suffix from `grammar_rules` table
  - `get_subject(gender)` → gets pronoun (நான், அவன்…) from DB
  - `save_sentence()` → writes to `saved_sentences` table
  - `get_saved()` → reads saved sentences
  - `delete_saved(id)` → deletes a saved sentence by ID

### `tamil_nlp.db` — The Memory (SQLite Database)
Contains **3 tables**:
- `vocabulary` — Tamil words, their English meanings, and category
- `grammar_rules` — Tense/gender suffix rules (e.g., present + first = கிறேன்)
- `saved_sentences` — Sentences the user saves from the app

### `.env` — Secret Keys File
```
GEMINI_API_KEY=...   ← Used for AI variations and chatbot
ANTHROPIC_API_KEY=... ← Fallback if Gemini fails
```
> ⚠️ **Note:** Your current `.env` has the keys swapped! The value starting with `AIzaSy...` is the Gemini key, but it's assigned to `ANTHROPIC_API_KEY`. Check and fix this.

---

## 🖥️ How the Frontend Files Work

### `index.html` — The Main Page
- Has a **left panel** (form inputs: noun, verb, tense, gender, type)
- Has a **right panel** (output display area — shows result or chat bubbles)
- Loads `style.css` and `main.js`
- Has **quick preset buttons** that auto-fill the form with example Tamil sentences

### `main.js` — The Frontend Logic (All Pages' JS)
Key functions and what they call:

| Function | Trigger | API Call |
|---|---|---|
| `generateSentence()` | "Generate" button click | `POST /generate` |
| `speakText()` | "Speak" button click | `POST /tts` |
| `saveSentence()` | "Save" button click | `POST /save` |
| `getVariations()` | "Variations" button click | `POST /variations` |
| `startVoiceInput()` | Mic button click | Uses browser's Web Speech API (no server call) |
| `setupTheme()` | Page load | Uses `localStorage` only (no server call) |

### `style.css` — All Visual Styling
- Dark/light mode support via `.dark-mode` / `.light-mode` CSS classes
- All layouts, animations, fonts, colors
- Tamil font: **Noto Sans Tamil** from Google Fonts

---

## 🔄 One Complete User Journey (Step-by-Step)

> **User types "பால்" as noun, "குடி" as verb, selects Present Tense, First Person, Statement → clicks Generate**

```
1. Browser (main.js):
   generateSentence() collects form values
   → fetch("POST /generate", { noun:"பால்", verb:"குடி", tense:"present", gender:"first", sentence_type:"statement" })

2. Flask (app.py):
   @route('/generate') receives the JSON
   → calls engine.generate_statement("பால்", "குடி", "present", "first")

3. grammar_engine.py:
   generate_statement() calls conjugate_verb("குடி", "present", "first")
   → _get_verb_stems("குடி") looks up SUPPORTED_VERBS["குடி"]
   → present_stem = "குடிக்கிற" + ending["first"] = "ேன்"
   → conjugated = "குடிக்கிறேன்"
   → sentence = "நான் பால் குடிக்கிறேன்"

4. app.py:
   Returns JSON: { "type": "statement", "output": "நான் பால் குடிக்கிறேன்" }

5. Browser (main.js):
   displayResults() receives the JSON
   → Shows "நான் பால் குடிக்கிறேன்" in the output panel

6. User clicks "Speak":
   speakText() calls fetch("POST /tts", { text: "நான் பால் குடிக்கிறேன்" })
   → app.py uses gTTS to generate Tamil audio
   → Returns MP3 bytes
   → Browser plays the audio through the hidden <audio> element
```