# backend/app.py
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import sys
import os
import io
import json
# pyrefly: ignore [missing-import]
from gtts import gTTS
from dotenv import load_dotenv

# Load environment secrets
load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from grammar_engine import TamilGrammarEngine
from db_manager import (
    get_all_vocabulary, search_vocabulary,
    save_sentence, get_saved, delete_saved,
    get_dialogues, get_daily_word,
    save_quiz_result, get_quiz_history,
    get_dashboard_stats, award_action_points
)


app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
# Allow all origins so the app works on Render
CORS(app, resources={r'/*': {'origins': '*'}})
engine = TamilGrammarEngine()


# ─────────────────────────────────────────────────────────
# Helper: call AI (disabled — returns fallback text)
# ─────────────────────────────────────────────────────────

def call_ai(prompt, system=None, max_tokens=600, fallback_text=None):
    """AI is disabled. Always returns the provided fallback text."""
    return fallback_text or "AI features are currently disabled."


# ─────────────────────────────────────────────────────────
# Phase 1: Core Pages
# ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json() or {}
        noun      = data.get('noun', '').strip()
        verb      = data.get('verb', '').strip()
        tense     = data.get('tense', 'present')
        gender    = data.get('gender', 'first')
        sent_type = data.get('sentence_type', 'statement')

        if not noun or not verb:
            return jsonify({'error': 'Both noun and verb are required.'}), 400

        if sent_type == 'statement':
            result = engine.generate_statement(noun, verb, tense, gender)
            award_action_points('generate')
            return jsonify({'type': 'statement', 'output': result})
        elif sent_type == 'question':
            result = engine.generate_question(noun, verb, tense, gender)
            award_action_points('generate')
            return jsonify({'type': 'question', 'output': result})
        elif sent_type == 'dialogue':
            result = engine.generate_dialogue(noun, verb, tense, gender)
            award_action_points('generate')
            return jsonify({'type': 'dialogue', 'output': result})
        else:
            return jsonify({'error': 'Invalid sentence type.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text is required for TTS.'}), 400
        fp = io.BytesIO()
        tts_obj = gTTS(text=text, lang='ta')
        tts_obj.write_to_fp(fp)
        fp.seek(0)
        return send_file(fp, mimetype='audio/mp3', as_attachment=False,
                         download_name='tamil_audio.mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────
# Phase 2: Database routes
# ─────────────────────────────────────────────────────────

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json() or {}
        sentence = data.get('sentence', '').strip()
        stype    = data.get('sentence_type', 'statement')
        tense    = data.get('tense', 'present')
        if not sentence:
            return jsonify({'error': 'Sentence content is required.'}), 400
        save_sentence(sentence, stype, tense)
        return jsonify({'status': 'saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/saved')
def saved_page():
    return render_template('saved.html')


@app.route('/api/saved')
def api_saved():
    try:
        return jsonify(get_saved())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/saved/<int:sid>', methods=['DELETE'])
def del_saved(sid):
    try:
        delete_saved(sid)
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vocabulary')
def vocab_page():
    return render_template('vocabulary.html')


@app.route('/api/vocabulary')
def api_vocab():
    try:
        q = request.args.get('search', '').strip()
        if q:
            return jsonify(search_vocabulary(q))
        return jsonify(get_all_vocabulary())
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ─────────────────────────────────────────────────────────
# G1: Grammar Checker
# ─────────────────────────────────────────────────────────

@app.route('/grammar')
def grammar_page():
    return render_template('grammar.html')


@app.route('/check_grammar', methods=['POST'])
def check_grammar():
    try:
        data = request.get_json() or {}
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text is required'}), 400

        prompt = f'''You are an expert Tamil grammar teacher.
Analyse this Tamil text: {text}
1. Identify any grammar errors (tense, verb agreement, case markers, word order).
2. Provide a corrected version.
3. Explain each correction in simple English.
If the sentence is already correct, say so and explain why it is correct.
Format your response clearly with sections: ORIGINAL, CORRECTED, EXPLANATION.'''

        result = call_ai(prompt, max_tokens=700,
                         fallback_text=(
                             f"ORIGINAL: {text}\n"
                             f"CORRECTED: {text}\n"
                             "EXPLANATION: AI grammar checker requires a GEMINI_API_KEY in backend/.env. "
                             "The sentence structure follows Subject-Object-Verb (SOV) order."
                         ))
        award_action_points('grammar_check')
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────
# G2: Dialogue Library
# ─────────────────────────────────────────────────────────

@app.route('/dialogues')
def dialogues_page():
    return render_template('dialogues.html')


@app.route('/api/dialogues')
def api_dialogues():
    try:
        scenario = request.args.get('scenario', '').strip()
        return jsonify(get_dialogues(scenario))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────
# G3: Daily Word
# ─────────────────────────────────────────────────────────

@app.route('/api/daily_word')
def daily_word():
    try:
        return jsonify(get_daily_word())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────
# G4: Quiz Engine
# ─────────────────────────────────────────────────────────

@app.route('/quiz')
def quiz_page():
    return render_template('quiz.html')


@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data  = request.get_json() or {}
        qtype = data.get('type', 'vocab')

        prompt = f'''Generate a Tamil {qtype} quiz with 5 multiple-choice questions for beginners.
Each question must include:
- A Tamil word, sentence, or grammar rule as the question
- 4 answer options (A, B, C, D) in English or Tamil
- The correct answer letter
- A short explanation (1 sentence)

Return ONLY a valid JSON array like this exact format:
[
  {{
    "question": "What does பால் mean?",
    "options": ["water", "milk", "rice", "bread"],
    "answer": "B",
    "explanation": "பால் (paal) means milk in Tamil."
  }}
]
No markdown, no extra text — only the JSON array.'''

        raw = call_ai(prompt, max_tokens=1000, fallback_text=None)

        if raw is None:
            # Built-in fallback quiz
            quiz = _fallback_quiz(qtype)
            return jsonify({'quiz': quiz})

        # Parse JSON from AI response
        try:
            clean = raw.strip()
            if '```' in clean:
                clean = clean.split('```')[1]
                if clean.startswith('json'):
                    clean = clean[4:]
            quiz = json.loads(clean.strip())
            return jsonify({'quiz': quiz})
        except (json.JSONDecodeError, IndexError):
            return jsonify({'quiz': _fallback_quiz(qtype)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _fallback_quiz(qtype):
    """Hardcoded fallback quiz when AI is unavailable."""
    if qtype == 'vocab':
        return [
            {"question": "What does 'பால்' (paal) mean?",
             "options": ["water", "milk", "rice", "bread"], "answer": "B",
             "explanation": "பால் (paal) means milk in Tamil."},
            {"question": "What does 'வீடு' (veedu) mean?",
             "options": ["school", "market", "house", "road"], "answer": "C",
             "explanation": "வீடு (veedu) means house in Tamil."},
            {"question": "What does 'புத்தகம்' (puththagam) mean?",
             "options": ["pen", "book", "bag", "table"], "answer": "B",
             "explanation": "புத்தகம் (puththagam) means book in Tamil."},
            {"question": "What does 'தண்ணீர்' (thanneer) mean?",
             "options": ["fire", "air", "earth", "water"], "answer": "D",
             "explanation": "தண்ணீர் (thanneer) means water in Tamil."},
            {"question": "What does 'பள்ளி' (palli) mean?",
             "options": ["school", "temple", "shop", "office"], "answer": "A",
             "explanation": "பள்ளி (palli) means school in Tamil."},
        ]
    else:  # grammar quiz
        return [
            {"question": "Tamil uses which word order?",
             "options": ["SVO (Subject-Verb-Object)", "SOV (Subject-Object-Verb)",
                         "VSO (Verb-Subject-Object)", "OVS"], "answer": "B",
             "explanation": "Tamil uses SOV order: நான் பால் குடிக்கிறேன் (I milk drink)."},
            {"question": "What is 'நான்' (naan)?",
             "options": ["He", "She", "I", "They"], "answer": "C",
             "explanation": "நான் (naan) is the first-person singular pronoun meaning 'I'."},
            {"question": "Present tense suffix for first person?",
             "options": ["கிறான்", "கிறேன்", "கிறாள்", "கிறது"], "answer": "B",
             "explanation": "கிறேன் is the present-tense suffix for first person (நான்)."},
            {"question": "What does 'அவள்' (aval) mean?",
             "options": ["He", "She", "It", "They"], "answer": "B",
             "explanation": "அவள் (aval) is the third-person feminine pronoun meaning 'She'."},
            {"question": "How do you say 'They drink milk' in Tamil?",
             "options": ["நான் பால் குடிக்கிறேன்", "அவன் பால் குடிக்கிறான்",
                         "அவர்கள் பால் குடிக்கிறார்கள்", "அது பால் குடிக்கிறது"],
             "answer": "C",
             "explanation": "அவர்கள் (they) + பால் (milk) + குடிக்கிறார்கள் (drink) = They drink milk."},
        ]


@app.route('/api/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        data = request.get_json() or {}
        quiz_type = data.get('quiz_type', 'vocab')
        score     = int(data.get('score', 0))
        total     = int(data.get('total', 0))
        save_quiz_result(quiz_type, score, total)
        award_action_points('quiz_complete')
        return jsonify({'status': 'saved', 'points_awarded': score * 20})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────
# G5: Dashboard
# ─────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/api/dashboard')
def api_dashboard():
    try:
        return jsonify(get_dashboard_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/award_points', methods=['POST'])
def api_award_points():
    try:
        data   = request.get_json() or {}
        action = data.get('action', 'generate')
        award_action_points(action)
        stats = get_dashboard_stats()
        return jsonify({'status': 'ok', 'total_points': stats['total_points']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
