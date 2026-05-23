# backend/app.py
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import sys
import os
import io
from gtts import gTTS

# Ensure backend directory is in python search path
sys.path.insert(0, os.path.dirname(__file__))
from grammar_engine import TamilGrammarEngine

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

if __name__ == '__main__':
    # Run on port 5000 in debug mode
    app.run(debug=True, port=5000)
