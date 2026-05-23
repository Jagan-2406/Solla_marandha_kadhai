# backend/test_grammar.py
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from grammar_engine import TamilGrammarEngine
from app import app

class TestTamilGrammar(unittest.TestCase):
    def setUp(self):
        self.engine = TamilGrammarEngine()
        self.client = app.test_client()

    def test_strong_verb_conjugation(self):
        # குடி (drink) - strong verb
        # Present Tense
        self.assertEqual(self.engine.conjugate_verb("குடி", "present", "first"), "குடிக்கிறேன்")
        self.assertEqual(self.engine.conjugate_verb("குடி", "present", "male"), "குடிக்கிறான்")
        self.assertEqual(self.engine.conjugate_verb("குடி", "present", "neutral"), "குடிக்கிறது")
        
        # Past Tense
        self.assertEqual(self.engine.conjugate_verb("குடி", "past", "first"), "குடித்தேன்")
        self.assertEqual(self.engine.conjugate_verb("குடி", "past", "male"), "குடித்தான்")
        self.assertEqual(self.engine.conjugate_verb("குடி", "past", "neutral"), "குடித்தது")
        
        # Future Tense
        self.assertEqual(self.engine.conjugate_verb("குடி", "future", "first"), "குடிப்பேன்")
        self.assertEqual(self.engine.conjugate_verb("குடி", "future", "male"), "குடிப்பான்")
        self.assertEqual(self.engine.conjugate_verb("குடி", "future", "neutral"), "குடிக்கும்")

    def test_weak_doubled_verb_conjugation(self):
        # சாப்பிடு (eat) - weak verb with doubled consonant in past
        # Present Tense
        self.assertEqual(self.engine.conjugate_verb("சாப்பிடு", "present", "first"), "சாப்பிடுகிறேன்")
        self.assertEqual(self.engine.conjugate_verb("சாப்பிடு", "present", "neutral"), "சாப்பிடுகிறது")
        
        # Past Tense
        self.assertEqual(self.engine.conjugate_verb("சாப்பிடு", "past", "first"), "சாப்பிட்டேன்")
        self.assertEqual(self.engine.conjugate_verb("சாப்பிடு", "past", "male"), "சாப்பிட்டான்")
        self.assertEqual(self.engine.conjugate_verb("சாப்பிடு", "past", "neutral"), "சாப்பிட்டது")

    def test_weak_in_verb_conjugation(self):
        # எழுது (write) - weak verb with 'in' in past
        self.assertEqual(self.engine.conjugate_verb("எழுது", "present", "first"), "எழுதுகிறேன்")
        self.assertEqual(self.engine.conjugate_verb("எழுது", "past", "first"), "எழுதினேன்")
        self.assertEqual(self.engine.conjugate_verb("எழுது", "future", "first"), "எழுதுவேன்")
        self.assertEqual(self.engine.conjugate_verb("எழுது", "future", "neutral"), "எழுதும்")

    def test_generate_statement(self):
        # Test basic statement generation
        stmt = self.engine.generate_statement("பால்", "குடி", "present", "first")
        self.assertEqual(stmt, "நான் பால் குடிக்கிறேன்")
        
        stmt2 = self.engine.generate_statement("சோறு", "சாப்பிடு", "past", "male")
        self.assertEqual(stmt2, "அவன் சோறு சாப்பிட்டான்")

    def test_generate_question(self):
        # Test question suffix generation
        qstn1 = self.engine.generate_question("பால்", "குடி", "present", "first")
        self.assertEqual(qstn1, "நான் பால் குடிக்கிறேனா?")

        qstn2 = self.engine.generate_question("சோறு", "சாப்பிடு", "past", "male")
        self.assertEqual(qstn2, "அவன் சோறு சாப்பிட்டானா?")
        
        qstn3 = self.engine.generate_question("நீர்", "குடி", "future", "neutral")
        self.assertEqual(qstn3, "அது நீர் குடிக்குமா?")

    def test_generate_dialogue(self):
        # Test dialogue structure
        dial = self.engine.generate_dialogue("பால்", "குடி", "present", "first")
        self.assertEqual(len(dial), 2)
        # Check first person question turns to "நீ ... கிறாயா?"
        self.assertEqual(dial[0]['speaker'], "நண்பன்")
        self.assertEqual(dial[0]['line'], "நீ பால் குடிக்கிறாயா?")
        self.assertEqual(dial[1]['speaker'], "நான்")
        self.assertEqual(dial[1]['line'], "ஆம், நான் பால் குடிக்கிறேன்")

    def test_flask_endpoints(self):
        # Test root serving
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

        # Test generate statement
        payload = {
            'noun': 'பால்',
            'verb': 'குடி',
            'tense': 'present',
            'gender': 'first',
            'sentence_type': 'statement'
        }
        resp = self.client.post('/generate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(data['type'], 'statement')
        self.assertEqual(data['output'], 'நான் பால் குடிக்கிறேன்')

        # Test validation error
        bad_payload = {
            'noun': '',
            'verb': 'குடி'
        }
        resp = self.client.post('/generate', data=json.dumps(bad_payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # Test TTS endpoint
        tts_payload = {'text': 'நான் தமிழ் படிக்கிறேன்'}
        resp = self.client.post('/tts', data=json.dumps(tts_payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, 'audio/mp3')

if __name__ == '__main__':
    unittest.main()
