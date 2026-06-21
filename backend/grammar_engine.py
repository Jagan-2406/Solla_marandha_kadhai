# backend/grammar_engine.py
# Tamil Grammar Engine - Rule-based Sentence Generator with Sandhi rules

SUPPORTED_VERBS = {
    'குடி': {
        'class': 'strong',
        'past_stem': 'குடித்த',
        'present_stem': 'குடிக்கிற',
        'future_stem': 'குடிப்ப',
        'neutral_future': 'குடிக்கும்',
        'neutral_present': 'குடிக்கிறது',
        'neutral_past': 'குடித்தது'
    },
    'படி': {
        'class': 'strong',
        'past_stem': 'படித்த',
        'present_stem': 'படிக்கிற',
        'future_stem': 'படிப்ப',
        'neutral_future': 'படிக்கும்',
        'neutral_present': 'படிக்கிறது',
        'neutral_past': 'படித்தது'
    },
    'செய்': {
        'class': 'weak_regular',
        'past_stem': 'செய்த',
        'present_stem': 'செய்கிற',
        'future_stem': 'செய்வ',
        'neutral_future': 'செய்யும்',
        'neutral_present': 'செய்கிறது',
        'neutral_past': 'செய்தது'
    },
    'சாப்பிடு': {
        'class': 'weak_doubled',
        'past_stem': 'சாப்பிட்ட',
        'present_stem': 'சாப்பிடுகிற',
        'future_stem': 'சாப்பிடுவ',
        'neutral_future': 'சாப்பிடும்',
        'neutral_present': 'சாப்பிடுகிறது',
        'neutral_past': 'சாப்பிட்டது'
    },
    'எழுது': {
        'class': 'weak_in',
        'past_stem': 'எழுதின',
        'present_stem': 'எழுதுகிற',
        'future_stem': 'எழுதுவ',
        'neutral_future': 'எழுதும்',
        'neutral_present': 'எழுதுகிறது',
        'neutral_past': 'எழுதினது'
    },
    'பாடு': {
        'class': 'weak_in',
        'past_stem': 'பாடின',
        'present_stem': 'பாடுகிற',
        'future_stem': 'பாடுவ',
        'neutral_future': 'பாடும்',
        'neutral_present': 'பாடுகிறது',
        'neutral_past': 'பாடினது'
    },
    'விளையாடு': {
        'class': 'weak_in',
        'past_stem': 'விளையாடின',
        'present_stem': 'விளையாடுகிற',
        'future_stem': 'விளையாடுவ',
        'neutral_future': 'விளையாடும்',
        'neutral_present': 'விளையாடுகிறது',
        'neutral_past': 'விளையாடினது'
    },
    'காண்': {
        'class': 'special',
        'past_stem': 'கண்ட',
        'present_stem': 'காண்கிற',
        'future_stem': 'காண்ப',
        'neutral_future': 'காணும்',
        'neutral_present': 'காண்கிறது',
        'neutral_past': 'கண்டது'
    },
    'போ': {
        'class': 'special',
        'past_stem': 'போன',
        'present_stem': 'போகிற',
        'future_stem': 'போவ',
        'neutral_future': 'போகும்',
        'neutral_present': 'போகிறது',
        'neutral_past': 'போனது'
    },
    'வா': {
        'class': 'special',
        'past_stem': 'வந்த',
        'present_stem': 'வருகிற',
        'future_stem': 'வருவ',
        'neutral_future': 'வரும்',
        'neutral_present': 'வருகிறது',
        'neutral_past': 'வந்தது'
    }
}

class TamilGrammarEngine:
    def __init__(self):
        # Pronouns (loaded from DB if available, fallback to defaults)
        try:
            from db_manager import get_subject
            self.subjects = {
                'first':  get_subject('first'),
                'male':   get_subject('male'),
                'female': get_subject('female'),
                'neutral': get_subject('neutral'),
                'plural': get_subject('plural')
            }
        except Exception:
            self.subjects = {
                'first':  'நான்',   # I
                'male':   'அவன்',   # He
                'female': 'அவள்',   # She
                'neutral':'அது',    # It
                'plural': 'அவர்கள்' # They / Plural / Honorific
            }

        # Endings by gender (except neutral)
        self.endings = {
            'first': 'ேன்',
            'male': 'ான்',
            'female': 'ாள்',
            'plural': 'ார்கள்'
        }

    def _get_verb_stems(self, verb):
        """
        Retrieves present, past, and future stems for a given verb root.
        Falls back to rule-based conjugation if verb is not pre-registered.
        """
        # Clean verb
        verb = verb.strip()
        
        if verb in SUPPORTED_VERBS:
            return SUPPORTED_VERBS[verb]
            
        # Fallback heuristic rules
        # 1. Determine if verb is strong or weak. 
        # Verbs ending in 'இ' or 'அ' or 'உ' with strong characteristics:
        is_strong = verb.endswith('இ') or verb.endswith('அ') or verb in ['பார்', 'கேள்', 'நட', 'தா']
        
        # 2. Check if verb ends in 'உ' for weak-in class (like 'எழுது', 'ஓடு')
        is_ends_u = verb.endswith('உ') and not is_strong
        
        if is_strong:
            return {
                'class': 'strong',
                'past_stem': verb + 'த்த',
                'present_stem': verb + 'க்கிற',
                'future_stem': verb + 'ப்ப',
                'neutral_future': verb + 'க்கும்',
                'neutral_present': verb + 'க்கிறது',
                'neutral_past': verb + 'த்தது'
            }
        elif is_ends_u:
            # Drop the last 'உ' to form stems
            base = verb[:-1]
            return {
                'class': 'weak_in',
                'past_stem': base + 'ின',
                'present_stem': verb + 'கிற',
                'future_stem': verb + 'வ',
                'neutral_future': base + 'ும்',
                'neutral_present': verb + 'க்கிறது' if verb.endswith('டு') and len(verb) <= 3 else verb + 'கிறது',
                'neutral_past': base + 'ினது'
            }
        else:
            # General weak regular fallback (like 'செய்')
            return {
                'class': 'weak_regular',
                'past_stem': verb + 'த',
                'present_stem': verb + 'கிற',
                'future_stem': verb + 'வ',
                'neutral_future': verb + 'ும்',
                'neutral_present': verb + 'கிறது',
                'neutral_past': verb + 'தது'
            }

    def conjugate_verb(self, verb, tense, gender):
        """Conjugates a verb root correctly based on tense and gender."""
        stems = self._get_verb_stems(verb)
        
        if gender == 'neutral':
            if tense == 'present':
                return stems['neutral_present']
            elif tense == 'past':
                return stems['neutral_past']
            else:
                return stems['neutral_future']
        
        # Non-neutral conjugation
        ending = self.endings.get(gender, 'ேன்')
        if tense == 'present':
            return stems['present_stem'] + ending
        elif tense == 'past':
            return stems['past_stem'] + ending
        else:
            return stems['future_stem'] + ending

    def generate_statement(self, noun, verb, tense, gender):
        """Generates a complete Tamil statement sentence."""
        subject = self.subjects.get(gender, 'நான்')
        conjugated = self.conjugate_verb(verb, tense, gender)
        
        # Format: Subject Noun Verb
        sentence = f"{subject} {noun} {conjugated}"
        return sentence

    def generate_question(self, noun, verb, tense, gender):
        """Generates a Tamil question (ends with question marker 'ஆ?')."""
        statement = self.generate_statement(noun, verb, tense, gender)
        
        # Conjugated verb ends with 'ேன்', 'ான்', 'ாள்', 'ார்கள்', 'து', 'ும்'
        # To make it a question:
        # - ends in 'து' -> 'தா?' (e.g. குடித்தது -> குடித்ததா?)
        # - ends in 'ும்' -> 'ுமா?' (e.g. குடிக்கும் -> குடிக்குமா?)
        # - ends in 'ன்'/'ள்' -> add 'ா?' (e.g. குடித்தான் -> குடித்தானா?)
        # - ends in 'கள்' -> add 'ா?' (e.g. குடித்தார்கள் -> குடித்தார்களா?)
        
        if statement.endswith('து'):
            question = statement[:-2] + 'தா?'
        elif statement.endswith('ம்'):
            question = statement[:-2] + 'மா?'
        elif statement.endswith('்'):
            # e.g., குடித்தேன் -> குடித்தேனா?, குடித்தான் -> குடித்தானா?, குடித்தாள் -> குடித்தாளா?
            question = statement[:-1] + 'ா?'
        elif statement.endswith('கள்'):
            # e.g., குடித்தார்கள் -> குடித்தார்களா?
            question = statement + 'ா?'
        else:
            # Fallback
            question = statement + 'ா?'
            
        return question

    def generate_dialogue(self, noun, verb, tense, gender):
        """Generates a dialogue exchange between a Friend and the Subject."""
        # The friend asks a question about the subject
        # e.g. "அவன் பால் குடிக்கிறானா?" (Is he drinking milk?)
        # The subject/speaker replies: "ஆம், அவன் பால் குடிக்கிறான்." (Yes, he is drinking milk.)
        qstn = self.generate_question(noun, verb, tense, gender)
        stmt = self.generate_statement(noun, verb, tense, gender)
        
        # Adjust subject for the response (if gender is 'first', answer is still 'நான்', 
        # but the question should ask 'நீ' (you)). Let's make it super natural!
        if gender == 'first':
            # Question: "நீ பால் குடிக்கிறாயா?" (Are you drinking milk?)
            # Response: "நான் பால் குடிக்கிறேன்." (I am drinking milk.)
            # Conjugate for second person ('நீ'): ending is 'ாய்' -> 'கிறாய்' -> 'கிறாயா?'
            stems = self._get_verb_stems(verb)
            if tense == 'present':
                verb_qstn = stems['present_stem'] + 'ாயா?'
            elif tense == 'past':
                verb_qstn = stems['past_stem'] + 'ாயா?'
            else:
                verb_qstn = stems['future_stem'] + 'ாயா?'
            
            # Formulate the question
            qstn = f"நீ {noun} {verb_qstn}"
            stmt = f"ஆம், {stmt}"
        else:
            stmt = f"ஆம், {stmt}"

        dialogue = [
            {'speaker': 'நண்பன்', 'line': qstn},
            {'speaker': self.subjects.get(gender, 'நான்'), 'line': stmt}
        ]
        return dialogue
