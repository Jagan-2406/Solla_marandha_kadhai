# backend/init_db.py
# Run ONCE to create all database tables and seed starter data.
# Run again to RESET the database (existing db is deleted).

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'tamil_nlp.db')

def init_database():
    # If DB already exists, delete and re-initialise
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database deleted. Re-initializing...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ─────────────────────────────────────────────────────────
    # Phase 2 Tables
    # ─────────────────────────────────────────────────────────

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            tamil_word      TEXT NOT NULL,
            english_meaning TEXT NOT NULL,
            category        TEXT NOT NULL,
            gender_class    TEXT,
            synonyms        TEXT DEFAULT '',
            antonyms        TEXT DEFAULT '',
            example_sentence TEXT DEFAULT '',
            difficulty      TEXT DEFAULT 'beginner'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammar_rules (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            tense   TEXT NOT NULL,
            gender  TEXT NOT NULL,
            suffix  TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_sentences (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence      TEXT NOT NULL,
            sentence_type TEXT NOT NULL,
            tense         TEXT NOT NULL,
            saved_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─────────────────────────────────────────────────────────
    # Part G — New Feature Tables
    # ─────────────────────────────────────────────────────────

    # G2: Dialogue Library
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogue_templates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario    TEXT NOT NULL,
            title       TEXT NOT NULL,
            speaker_a   TEXT NOT NULL,
            speaker_b   TEXT NOT NULL,
            english_a   TEXT NOT NULL,
            english_b   TEXT NOT NULL,
            difficulty  TEXT DEFAULT 'beginner'
        )
    ''')

    # G4: Quiz Engine — results storage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_type   TEXT,
            score       INTEGER,
            total       INTEGER,
            taken_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # G5: Gamification — points, streak, badges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_points (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            total_points INTEGER DEFAULT 0,
            streak_days  INTEGER DEFAULT 0,
            last_active  DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT NOT NULL,
            icon        TEXT NOT NULL,
            threshold   INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_id   INTEGER NOT NULL,
            earned_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (badge_id) REFERENCES badges(id)
        )
    ''')

    # ─────────────────────────────────────────────────────────
    # Seed Data
    # ─────────────────────────────────────────────────────────

    # Vocabulary (G3: now with synonyms, antonyms, example_sentence, difficulty)
    vocab_items = [
        # Nouns
        ('பால்',          'milk',     'noun', 'neutral', 'தாய்ப்பால்',     'தண்ணீர்',   'நான் தினமும் பால் குடிக்கிறேன்.',     'beginner'),
        ('சோறு',          'rice',     'noun', 'neutral', 'அரிசி,உணவு',    '',           'அவன் சோறு சாப்பிட்டான்.',              'beginner'),
        ('தண்ணீர்',       'water',    'noun', 'neutral', 'நீர்,ஜலம்',     '',           'அவள் தண்ணீர் குடிக்கிறாள்.',          'beginner'),
        ('புத்தகம்',      'book',     'noun', 'neutral', 'நூல்,ஏடு',      '',           'நான் புத்தகம் படிக்கிறேன்.',           'beginner'),
        ('பள்ளி',         'school',   'noun', 'neutral', 'பாடசாலை',       'வீடு',       'அவள் பள்ளிக்கு போகிறாள்.',             'beginner'),
        ('வீடு',          'house',    'noun', 'neutral', 'இல்லம்,மனை',   'பள்ளி',      'இது என் வீடு.',                         'beginner'),
        ('பாடம்',         'lesson',   'noun', 'neutral', 'படிப்பு',       '',           'நான் பாடம் படிக்கிறேன்.',               'beginner'),
        ('பாடல்',         'song',     'noun', 'neutral', 'இசை,கீதம்',    '',           'அவள் பாடல் பாடுகிறாள்.',               'beginner'),
        ('திரைப்படம்',   'movie',    'noun', 'neutral', 'படம்',          '',           'நான் திரைப்படம் பார்க்கிறேன்.',         'intermediate'),
        ('விளையாட்டு',   'game',     'noun', 'neutral', 'ஆட்டம்',       '',           'அவன் விளையாட்டு விளையாடுகிறான்.',       'beginner'),
        ('மரம்',          'tree',     'noun', 'neutral', 'விருட்சம்',    '',           'அந்த மரம் பெரியது.',                     'beginner'),
        ('காற்று',        'wind',     'noun', 'neutral', 'வாயு',         '',           'காற்று வீசுகிறது.',                      'beginner'),
        ('சந்தை',         'market',   'noun', 'neutral', 'கடை,பேட்டை',  '',           'அம்மா சந்தைக்கு போகிறார்.',              'beginner'),
        ('வகுப்பு',       'class',    'noun', 'neutral', 'பாடம்',        '',           'வகுப்பு தொடங்குகிறது.',                  'intermediate'),
        ('நண்பன்',        'friend',   'noun', 'neutral', 'தோழன்',        'எதிரி',      'அவன் என் நண்பன்.',                      'beginner'),
        # Verbs
        ('குடி',          'drink',    'verb', 'neutral', 'அருந்து',       '',           'நான் பால் குடிக்கிறேன்.',               'beginner'),
        ('சாப்பிடு',      'eat',      'verb', 'neutral', 'உண்',          '',           'அவன் சோறு சாப்பிடுகிறான்.',             'beginner'),
        ('படி',           'study',    'verb', 'neutral', 'கற்று',        '',           'நான் பாடம் படிக்கிறேன்.',               'beginner'),
        ('எழுது',         'write',    'verb', 'neutral', '',              '',           'அவள் கடிதம் எழுதுகிறாள்.',              'beginner'),
        ('பாடு',          'sing',     'verb', 'neutral', '',              '',           'அவள் பாடல் பாடுகிறாள்.',               'beginner'),
        ('விளையாடு',     'play',     'verb', 'neutral', 'ஆடு',          '',           'அவன் விளையாடுகிறான்.',                   'beginner'),
        ('ஓடு',           'run',      'verb', 'neutral', '',              '',           'நான் வேகமாக ஓடுகிறேன்.',                'beginner'),
        ('பேசு',          'speak',    'verb', 'neutral', 'சொல்',         'மவுனமாயிரு', 'அவன் தமிழில் பேசுகிறான்.',              'beginner'),
        ('பார்',          'see',      'verb', 'neutral', 'காண்',         '',           'நான் திரைப்படம் பார்க்கிறேன்.',         'beginner'),
        ('போ',            'go',       'verb', 'neutral', 'செல்',         'வா',         'அவள் பள்ளிக்கு போகிறாள்.',              'beginner'),
        ('வா',            'come',     'verb', 'neutral', '',              'போ',         'அவன் வீட்டிற்கு வருகிறான்.',            'beginner'),
        ('செய்',          'do',       'verb', 'neutral', '',              '',           'நான் வீட்டு வேலை செய்கிறேன்.',          'beginner'),
        ('கேள்',          'listen',   'verb', 'neutral', 'கேட்டுக்கொள்', '',           'நீ கவனமாக கேள்.',                       'beginner'),
    ]
    cursor.executemany(
        '''INSERT INTO vocabulary
           (tamil_word, english_meaning, category, gender_class,
            synonyms, antonyms, example_sentence, difficulty)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        vocab_items
    )

    # Grammar rules
    rules = [
        ('present', 'first',   'கிறேன்',    'நான்'),
        ('present', 'male',    'கிறான்',    'அவன்'),
        ('present', 'female',  'கிறாள்',    'அவள்'),
        ('present', 'neutral', 'கிறது',     'அது'),
        ('present', 'plural',  'கிறார்கள்', 'அவர்கள்'),
        ('past',    'first',   'னேன்',      'நான்'),
        ('past',    'male',    'னான்',      'அவன்'),
        ('past',    'female',  'னாள்',      'அவள்'),
        ('past',    'neutral', 'னது',       'அது'),
        ('past',    'plural',  'னார்கள்',   'அவர்கள்'),
        ('future',  'first',   'வேன்',      'நான்'),
        ('future',  'male',    'வான்',      'அவன்'),
        ('future',  'female',  'வாள்',      'அவள்'),
        ('future',  'neutral', 'கும்',      'அது'),
        ('future',  'plural',  'வார்கள்',   'அவர்கள்'),
    ]
    cursor.executemany(
        'INSERT INTO grammar_rules (tense, gender, suffix, subject) VALUES (?, ?, ?, ?)',
        rules
    )

    # G2: Dialogue library — real-life Tamil conversations
    dialogues = [
        # School scenario
        ('school', 'Asking for a pen',
         'பேனா கொடுக்க முடியுமா?', 'இதோ, வாங்கிக்கோ.',
         'Can you give me a pen?', 'Here, take it.', 'beginner'),
        ('school', 'Asking teacher a question',
         'ஆசிரியரே, இந்தக் கேள்விக்கு விடை என்ன?', 'நல்ல கேள்வி! விடை இதுதான்.',
         'Teacher, what is the answer to this question?', 'Good question! The answer is this.', 'beginner'),
        ('school', 'Making a new friend',
         'நான் அர்ஜுன். உன் பெயர் என்ன?', 'என் பெயர் பிரியா. நன்றாக இருக்கிறேன்.',
         'I am Arjun. What is your name?', 'My name is Priya. I am doing well.', 'beginner'),
        # Daily life
        ('daily', 'Buying vegetables',
         'வெங்காயம் எவ்வளவு?', 'கிலோ பத்து ரூபாய்.',
         'How much is onion?', 'Ten rupees per kilo.', 'beginner'),
        ('daily', 'Morning greeting',
         'காலை வணக்கம்! எப்படி இருக்கீங்க?', 'நன்றாக இருக்கிறேன். நீங்கள்?',
         'Good morning! How are you?', 'I am fine. And you?', 'beginner'),
        ('daily', 'Asking for directions',
         'பஸ் நிறுத்தம் எங்கே இருக்கிறது?', 'நேராக போங்கள், இடது பக்கம் திரும்புங்கள்.',
         'Where is the bus stop?', 'Go straight and turn left.', 'beginner'),
        ('daily', 'At the doctor',
         'டாக்டர், எனக்கு காய்ச்சல் இருக்கிறது.', 'கவலைப்படாதீர்கள். மருந்து சாப்பிடுங்கள்.',
         'Doctor, I have a fever.', 'Do not worry. Take the medicine.', 'intermediate'),
        # Office
        ('office', 'Good morning greeting',
         'காலை வணக்கம் சார்.', 'வணக்கம், எப்படி இருக்கீங்க?',
         'Good morning sir.', 'Hello, how are you?', 'beginner'),
        ('office', 'Meeting time',
         'கூட்டம் எத்தனை மணிக்கு?', 'மூன்று மணிக்கு கூட்டம் இருக்கிறது.',
         'What time is the meeting?', 'The meeting is at 3 o\'clock.', 'intermediate'),
        ('office', 'Asking for leave',
         'சார், நாளைக்கு விடுமுறை கொடுக்க முடியுமா?', 'சரி, போய் வாருங்கள்.',
         'Sir, can I take leave tomorrow?', 'Okay, you may go.', 'intermediate'),
        # Interview
        ('interview', 'Self introduction',
         'என் பெயர் ஜெயன். நான் கணினி படிச்சேன்.',
         'நல்லது. அனுபவம் ஏதாவது இருக்கா?',
         'My name is Jayan. I studied computer science.',
         'Good. Do you have any experience?', 'intermediate'),
        ('interview', 'Strength and weakness',
         'என் பலம் கடினமாக உழைப்பது.',
         'அது நல்லது. பலவீனம் என்ன?',
         'My strength is hard work.',
         'That is good. What is your weakness?', 'intermediate'),
        # Family
        ('family', 'Introducing family',
         'இவர் என் அம்மா. அவர் ஆசிரியர்.',
         'வணக்கம் அம்மா. உங்கள் மகன் மிகவும் திறமையானவர்.',
         'This is my mother. She is a teacher.',
         'Hello madam. Your son is very talented.', 'beginner'),
        ('family', 'Dinner conversation',
         'அம்மா, இன்று என்ன சமைத்தீர்கள்?',
         'சாம்பார் சாதம் சமைத்தேன்.',
         'Mom, what did you cook today?',
         'I cooked sambar rice.', 'beginner'),
    ]
    cursor.executemany(
        '''INSERT INTO dialogue_templates
           (scenario, title, speaker_a, speaker_b, english_a, english_b, difficulty)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        dialogues
    )

    # G5: Badges definition
    badges = [
        ('First Sentence', 'Generated your first Tamil sentence!', '🌟', 1),
        ('Word Saver', 'Saved 5 sentences to your collection.', '💾', 5),
        ('Tamil Talker', 'Used the AI Tutor 10 times.', '💬', 10),
        ('Quiz Starter', 'Completed your first quiz!', '📝', 1),
        ('High Scorer', 'Scored 100% in a quiz.', '🏆', 100),
        ('Daily Learner', 'Maintained a 3-day learning streak.', '🔥', 3),
        ('Grammar Guru', 'Checked grammar 5 times.', '✅', 5),
        ('Dialogue Master', 'Practiced 10 dialogues.', '🗣️', 10),
    ]
    cursor.executemany(
        'INSERT INTO badges (name, description, icon, threshold) VALUES (?, ?, ?, ?)',
        badges
    )

    # Initialise the user_points row (single-user app)
    from datetime import date
    cursor.execute(
        'INSERT INTO user_points (total_points, streak_days, last_active) VALUES (0, 0, ?)',
        (str(date.today()),)
    )

    conn.commit()
    conn.close()
    print("SQLite database successfully created and seeded: backend/tamil_nlp.db")
    print("Tables created: vocabulary, grammar_rules, saved_sentences,")
    print("                dialogue_templates, quiz_results, user_points, badges, user_badges")

if __name__ == '__main__':
    init_database()
