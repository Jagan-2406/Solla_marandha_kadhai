# backend/init_db.py
# Run ONCE to create all PostgreSQL tables in Supabase and seed starter data.
# Usage: set DATABASE_URL env var, then run: python backend/init_db.py

import psycopg2
import os
from datetime import date

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set.\n"
        "Set it to your Supabase connection string:\n"
        "  $env:DATABASE_URL='postgresql://user:password@host:5432/postgres'"
    )


def init_database():
    print("Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("Dropping old tables (if any)...")
    cursor.execute('''
        DROP TABLE IF EXISTS user_badges CASCADE;
        DROP TABLE IF EXISTS badges CASCADE;
        DROP TABLE IF EXISTS user_points CASCADE;
        DROP TABLE IF EXISTS quiz_results CASCADE;
        DROP TABLE IF EXISTS dialogue_templates CASCADE;
        DROP TABLE IF EXISTS saved_sentences CASCADE;
        DROP TABLE IF EXISTS grammar_rules CASCADE;
        DROP TABLE IF EXISTS vocabulary CASCADE;
    ''')

    # ─────────────────────────────────────────────────────────
    # Create Tables
    # ─────────────────────────────────────────────────────────

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id              SERIAL PRIMARY KEY,
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
            id      SERIAL PRIMARY KEY,
            tense   TEXT NOT NULL,
            gender  TEXT NOT NULL,
            suffix  TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_sentences (
            id            SERIAL PRIMARY KEY,
            sentence      TEXT NOT NULL,
            sentence_type TEXT NOT NULL,
            tense         TEXT NOT NULL,
            saved_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialogue_templates (
            id          SERIAL PRIMARY KEY,
            scenario    TEXT NOT NULL,
            title       TEXT NOT NULL,
            speaker_a   TEXT NOT NULL,
            speaker_b   TEXT NOT NULL,
            english_a   TEXT NOT NULL,
            english_b   TEXT NOT NULL,
            difficulty  TEXT DEFAULT 'beginner'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id          SERIAL PRIMARY KEY,
            quiz_type   TEXT,
            score       INTEGER,
            total       INTEGER,
            taken_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_points (
            id           SERIAL PRIMARY KEY,
            total_points INTEGER DEFAULT 0,
            streak_days  INTEGER DEFAULT 0,
            last_active  DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id          SERIAL PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT NOT NULL,
            icon        TEXT NOT NULL,
            threshold   INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id         SERIAL PRIMARY KEY,
            badge_id   INTEGER NOT NULL REFERENCES badges(id),
            earned_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─────────────────────────────────────────────────────────
    # Seed Data
    # ─────────────────────────────────────────────────────────

    print("Seeding vocabulary...")
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
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
        vocab_items
    )

    print("Seeding grammar rules...")
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
        'INSERT INTO grammar_rules (tense, gender, suffix, subject) VALUES (%s, %s, %s, %s)',
        rules
    )

    print("Seeding dialogues...")
    dialogues = [
        ('school', 'Asking for a pen',
         'பேனா கொடுக்க முடியுமா?', 'இதோ, வாங்கிக்கோ.',
         'Can you give me a pen?', 'Here, take it.', 'beginner'),
        ('school', 'Asking teacher a question',
         'ஆசிரியரே, இந்தக் கேள்விக்கு விடை என்ன?', 'நல்ல கேள்வி! விடை இதுதான்.',
         'Teacher, what is the answer to this question?', 'Good question! The answer is this.', 'beginner'),
        ('school', 'Making a new friend',
         'நான் அர்ஜுன். உன் பெயர் என்ன?', 'என் பெயர் பிரியா. நன்றாக இருக்கிறேன்.',
         'I am Arjun. What is your name?', 'My name is Priya. I am doing well.', 'beginner'),
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
        ('office', 'Good morning greeting',
         'காலை வணக்கம் சார்.', 'வணக்கம், எப்படி இருக்கீங்க?',
         'Good morning sir.', 'Hello, how are you?', 'beginner'),
        ('office', 'Meeting time',
         'கூட்டம் எத்தனை மணிக்கு?', 'மூன்று மணிக்கு கூட்டம் இருக்கிறது.',
         'What time is the meeting?', 'The meeting is at 3 o\'clock.', 'intermediate'),
        ('office', 'Asking for leave',
         'சார், நாளைக்கு விடுமுறை கொடுக்க முடியுமா?', 'சரி, போய் வாருங்கள்.',
         'Sir, can I take leave tomorrow?', 'Okay, you may go.', 'intermediate'),
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
           VALUES (%s, %s, %s, %s, %s, %s, %s)''',
        dialogues
    )

    print("Seeding badges...")
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
        'INSERT INTO badges (name, description, icon, threshold) VALUES (%s, %s, %s, %s)',
        badges
    )

    print("Seeding initial user_points row...")
    cursor.execute(
        'INSERT INTO user_points (total_points, streak_days, last_active) VALUES (0, 0, %s)',
        (str(date.today()),)
    )

    conn.commit()
    conn.close()
    print("\nSUCCESS: Supabase PostgreSQL database successfully created and seeded!")
    print("Tables: vocabulary, grammar_rules, saved_sentences,")
    print("        dialogue_templates, quiz_results, user_points, badges, user_badges")


if __name__ == '__main__':
    init_database()
