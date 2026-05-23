# backend/app.py
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import sys
import os
import io
from gtts import gTTS
from dotenv import load_dotenv
import anthropic as ant

# Ensure backend directory is in python search path
sys.path.insert(0, os.path.dirname(__file__))
from grammar_engine import TamilGrammarEngine
from db_manager import (
    get_all_vocabulary, search_vocabulary,
    save_sentence, get_saved, delete_saved
)

# Load environment secrets
load_dotenv()
api_key = os.environ.get('ANTHROPIC_API_KEY')
gemini_key = os.environ.get('GEMINI_API_KEY') or api_key

ai_client = None
gemini_enabled = False

# Try importing google.generativeai defensively
try:
    import google.generativeai as genai
    if gemini_key and gemini_key.startswith('AIzaSy'):
        genai.configure(api_key=gemini_key)
        gemini_enabled = True
except ImportError:
    print("google-generativeai not installed yet. Running in mock fallback mode.")
except Exception as e:
    print(f"Error configuring Gemini: {e}")

if not gemini_enabled and api_key and not api_key.startswith('sk-ant-your-key') and api_key.startswith('sk-ant-'):
    ai_client = ant.Anthropic(api_key=api_key)

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
CORS(app)
engine = TamilGrammarEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json() or {}
        noun       = data.get('noun', '').strip()
        verb       = data.get('verb', '').strip()
        tense      = data.get('tense', 'present')
        gender     = data.get('gender', 'first')
        sent_type  = data.get('sentence_type', 'statement')

        if not noun or not verb:
            return jsonify({'error': 'Both noun and verb are required.'}), 400

        if sent_type == 'statement':
            result = engine.generate_statement(noun, verb, tense, gender)
            return jsonify({'type': 'statement', 'output': result})
        elif sent_type == 'question':
            result = engine.generate_question(noun, verb, tense, gender)
            return jsonify({'type': 'question', 'output': result})
        elif sent_type == 'dialogue':
            result = engine.generate_dialogue(noun, verb, tense, gender)
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
            
        # Create bytes stream in memory
        fp = io.BytesIO()
        tts_obj = gTTS(text=text, lang='ta')
        tts_obj.write_to_fp(fp)
        fp.seek(0)
        
        return send_file(
            fp, 
            mimetype='audio/mp3', 
            as_attachment=False,
            download_name='tamil_audio.mp3'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json() or {}
        sentence = data.get('sentence', '').strip()
        stype = data.get('sentence_type', 'statement')
        tense = data.get('tense', 'present')
        
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

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/variations', methods=['POST'])
def variations():
    try:
        data = request.get_json() or {}
        sent = data.get('sentence', '').strip()
        if not sent:
            return jsonify({'error': 'Sentence is required'}), 400
            
        if not ai_client:
            # Fallback high-quality Tamil language learning variations if no key is configured
            return jsonify({
                'variations': (
                    "1. " + sent + " தான் (Emphatic statement - Indeed this is what it is)\n"
                    "2. " + sent.replace("நான்", "என்னால்").replace("குடிக்கிறேன்", "குடிக்கப்பட்டது") + " (Passive voice format)\n"
                    "3. " + sent + " என்று நினைக்கிறேன் (Conjectural format - I think that...)"
                )
            })
            
        prompt = f'''You are a Tamil language teacher.
The student generated this Tamil sentence: {sent}
Give 3 alternative ways to express the same meaning in Tamil.
Format: number each line. Tamil sentence first, then English meaning in brackets.
Keep it simple for beginners.'''
        
        msg = ai_client.messages.create(
            model='claude-3-5-sonnet-latest',
            max_tokens=400,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return jsonify({'variations': msg.content[0].text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        user_msg = data.get('message', '').strip()
        history = data.get('history', [])
        
        if not user_msg:
            return jsonify({'error': 'Message is required'}), 400
            
        if not ai_client:
            # High-quality educational chatbot fallback responses
            lower_msg = user_msg.lower()
            if "hello" in lower_msg or "வணக்கம்" in lower_msg:
                reply = "வணக்கம்! Hello! I am Amma. Ask me about Tamil grammar (like 'verb conjugation' or 'noun rules')."
            elif "verbs" in lower_msg or "verb" in lower_msg:
                reply = "In Tamil, verbs come at the end of the sentence. For example: நான் (Subject) + பால் (Object) + குடிக்கிறேன் (Verb)."
            elif "tense" in lower_msg or "present" in lower_msg:
                reply = "Present tense uses the marker 'கிற' (kira). Example: படிக்கிறேன் (pa-di-kki-ren - I study/read)."
            else:
                reply = f"வணக்கம்! I received: '{user_msg}'. Set your ANTHROPIC_API_KEY in backend/.env to unlock interactive Claude AI learning sessions!"
            return jsonify({'reply': reply})
            
        system = '''You are a friendly Tamil language tutor named 'Amma'.
You help beginners learn Tamil grammar and sentences.
Reply in simple English with Tamil examples.
Always include the Tamil script alongside transliteration.
Keep answers short — 2 to 4 sentences max.'''
        
        formatted_history = []
        for h in history:
            formatted_history.append({'role': h.get('role', 'user'), 'content': h.get('content', '')})
            
        messages = formatted_history + [{'role': 'user', 'content': user_msg}]
        
        msg = ai_client.messages.create(
            model='claude-3-5-sonnet-latest',
            max_tokens=300,
            system=system,
            messages=messages
        )
        return jsonify({'reply': msg.content[0].text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000 in debug mode
    app.run(debug=True, port=5000)
