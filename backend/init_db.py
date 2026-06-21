# backend/init_db.py
# Run ONCE to create all PostgreSQL tables in Supabase and seed starter data.
# Usage: python backend/init_db.py  (reads DATABASE_URL from backend/.env)

import pg8000
import os
from datetime import date
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

# Load DATABASE_URL from backend/.env automatically
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set.\n"
        "Add it to backend/.env or set it in Render dashboard."
    )


def _parse_url(url):
    p = urlparse(url)
    return {
        'host':     p.hostname,
        'port':     p.port or 5432,
        'database': p.path.lstrip('/'),
        'user':     unquote(p.username or ''),
        'password': unquote(p.password or ''),
        'ssl_context': True,
    }


def init_database():
    print("Connecting to Supabase PostgreSQL...")
    db = pg8000.connect(**_parse_url(DATABASE_URL))
    cur = db.cursor()

    print("Dropping old tables (if any)...")
    cur.execute('DROP TABLE IF EXISTS user_badges CASCADE')
    cur.execute('DROP TABLE IF EXISTS badges CASCADE')
    cur.execute('DROP TABLE IF EXISTS user_points CASCADE')
    cur.execute('DROP TABLE IF EXISTS quiz_results CASCADE')
    cur.execute('DROP TABLE IF EXISTS dialogue_templates CASCADE')
    cur.execute('DROP TABLE IF EXISTS saved_sentences CASCADE')
    cur.execute('DROP TABLE IF EXISTS grammar_rules CASCADE')
    cur.execute('DROP TABLE IF EXISTS vocabulary CASCADE')
    db.commit()

    print("Creating tables...")
    cur.execute('''CREATE TABLE vocabulary (
        id              SERIAL PRIMARY KEY,
        tamil_word      TEXT NOT NULL,
        english_meaning TEXT NOT NULL,
        category        TEXT NOT NULL,
        gender_class    TEXT,
        synonyms        TEXT DEFAULT '',
        antonyms        TEXT DEFAULT '',
        example_sentence TEXT DEFAULT '',
        difficulty      TEXT DEFAULT 'beginner'
    )''')

    cur.execute('''CREATE TABLE grammar_rules (
        id      SERIAL PRIMARY KEY,
        tense   TEXT NOT NULL,
        gender  TEXT NOT NULL,
        suffix  TEXT NOT NULL,
        subject TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE saved_sentences (
        id            SERIAL PRIMARY KEY,
        sentence      TEXT NOT NULL,
        sentence_type TEXT NOT NULL,
        tense         TEXT NOT NULL,
        saved_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE dialogue_templates (
        id          SERIAL PRIMARY KEY,
        scenario    TEXT NOT NULL,
        title       TEXT NOT NULL,
        speaker_a   TEXT NOT NULL,
        speaker_b   TEXT NOT NULL,
        english_a   TEXT NOT NULL,
        english_b   TEXT NOT NULL,
        difficulty  TEXT DEFAULT 'beginner'
    )''')

    cur.execute('''CREATE TABLE quiz_results (
        id          SERIAL PRIMARY KEY,
        quiz_type   TEXT,
        score       INTEGER,
        total       INTEGER,
        taken_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''CREATE TABLE user_points (
        id           SERIAL PRIMARY KEY,
        total_points INTEGER DEFAULT 0,
        streak_days  INTEGER DEFAULT 0,
        last_active  DATE
    )''')

    cur.execute('''CREATE TABLE badges (
        id          SERIAL PRIMARY KEY,
        name        TEXT NOT NULL,
        description TEXT NOT NULL,
        icon        TEXT NOT NULL,
        threshold   INTEGER NOT NULL
    )''')

    cur.execute('''CREATE TABLE user_badges (
        id         SERIAL PRIMARY KEY,
        badge_id   INTEGER NOT NULL REFERENCES badges(id),
        earned_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()

    print("Seeding vocabulary...")
    vocab_items = [
        ('paal',         'milk',    'noun', 'neutral', '', 'thanneer', 'Naan thinanum paal kudikkiren.',  'beginner'),
        ('soru',         'rice',    'noun', 'neutral', '', '',          'Avan soru saapittaan.',           'beginner'),
        ('thanneer',     'water',   'noun', 'neutral', '', '',          'Aval thanneer kudikkiral.',       'beginner'),
        ('puthagam',     'book',    'noun', 'neutral', '', '',          'Naan puthagam padikkiren.',       'beginner'),
        ('palli',        'school',  'noun', 'neutral', '', 'veedu',    'Aval palliku pogiral.',            'beginner'),
        ('veedu',        'house',   'noun', 'neutral', '', 'palli',    'Idhu en veedu.',                   'beginner'),
        ('paadam',       'lesson',  'noun', 'neutral', '', '',          'Naan paadam padikkiren.',         'beginner'),
        ('paadal',       'song',    'noun', 'neutral', '', '',          'Aval paadal paadugiral.',         'beginner'),
        ('thirai padam', 'movie',   'noun', 'neutral', '', '',          'Naan thirai padam paarkkiren.',   'intermediate'),
        ('vilayaattu',   'game',    'noun', 'neutral', '', '',          'Avan vilayaattu vilayaadugiran.', 'beginner'),
        ('maram',        'tree',    'noun', 'neutral', '', '',          'Andha maram periyathu.',          'beginner'),
        ('kaatru',       'wind',    'noun', 'neutral', '', '',          'Kaatru veesugidhu.',              'beginner'),
        ('sandhai',      'market',  'noun', 'neutral', '', '',          'Amma sandhaiku pogiral.',         'beginner'),
        ('vagupu',       'class',   'noun', 'neutral', '', '',          'Vagupu thudangirathu.',           'intermediate'),
        ('nanban',       'friend',  'noun', 'neutral', '', 'pagai',    'Avan en nanban.',                  'beginner'),
        ('kudi',         'drink',   'verb', 'neutral', '', '',          'Naan paal kudikkiren.',           'beginner'),
        ('saapidu',      'eat',     'verb', 'neutral', '', '',          'Avan soru saapidugiran.',         'beginner'),
        ('padi',         'study',   'verb', 'neutral', '', '',          'Naan paadam padikkiren.',         'beginner'),
        ('ezhuthu',      'write',   'verb', 'neutral', '', '',          'Aval kadidham ezhudugiral.',      'beginner'),
        ('paadu',        'sing',    'verb', 'neutral', '', '',          'Aval paadal paadugiral.',         'beginner'),
        ('vilayaadu',    'play',    'verb', 'neutral', '', '',          'Avan vilayaadugiran.',            'beginner'),
        ('odu',          'run',     'verb', 'neutral', '', '',          'Naan vegamaga odugiren.',         'beginner'),
        ('pesu',         'speak',   'verb', 'neutral', '', '',          'Avan tamilil pesugiran.',         'beginner'),
        ('paar',         'see',     'verb', 'neutral', '', '',          'Naan thirai padam paarkkiren.',   'beginner'),
        ('po',           'go',      'verb', 'neutral', '', 'vaa',      'Aval palliku pogiral.',            'beginner'),
        ('vaa',          'come',    'verb', 'neutral', '', 'po',       'Avan veetukku varugiran.',         'beginner'),
        ('sei',          'do',      'verb', 'neutral', '', '',          'Naan veetu velai seigiren.',      'beginner'),
        ('kel',          'listen',  'verb', 'neutral', '', '',          'Nee kavanama kel.',               'beginner'),
    ]
    cur.executemany(
        'INSERT INTO vocabulary (tamil_word, english_meaning, category, gender_class, synonyms, antonyms, example_sentence, difficulty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        vocab_items
    )

    print("Seeding grammar rules...")
    rules = [
        ('present', 'first',   'kiren',    'Naan'),
        ('present', 'male',    'kiran',    'Avan'),
        ('present', 'female',  'kiral',    'Aval'),
        ('present', 'neutral', 'kirathu',  'Adhu'),
        ('present', 'plural',  'kirangal', 'Avargal'),
        ('past',    'first',   'nen',      'Naan'),
        ('past',    'male',    'nan',      'Avan'),
        ('past',    'female',  'nal',      'Aval'),
        ('past',    'neutral', 'nathu',    'Adhu'),
        ('past',    'plural',  'nargal',   'Avargal'),
        ('future',  'first',   'ven',      'Naan'),
        ('future',  'male',    'van',      'Avan'),
        ('future',  'female',  'val',      'Aval'),
        ('future',  'neutral', 'kum',      'Adhu'),
        ('future',  'plural',  'vargal',   'Avargal'),
    ]
    cur.executemany(
        'INSERT INTO grammar_rules (tense, gender, suffix, subject) VALUES (%s, %s, %s, %s)',
        rules
    )

    print("Seeding dialogues...")
    dialogues = [
        ('school', 'Asking for a pen', 'Can you give me a pen?', 'Here, take it.', 'Can you give me a pen?', 'Here, take it.', 'beginner'),
        ('school', 'Asking teacher', 'Teacher, what is the answer?', 'Good question!', 'Teacher, what is the answer?', 'Good question!', 'beginner'),
        ('school', 'Making a new friend', 'I am Arjun. What is your name?', 'My name is Priya.', 'I am Arjun. What is your name?', 'My name is Priya.', 'beginner'),
        ('daily', 'Buying vegetables', 'How much is onion?', 'Ten rupees per kilo.', 'How much is onion?', 'Ten rupees per kilo.', 'beginner'),
        ('daily', 'Morning greeting', 'Good morning! How are you?', 'I am fine. And you?', 'Good morning! How are you?', 'I am fine. And you?', 'beginner'),
        ('daily', 'Asking directions', 'Where is the bus stop?', 'Go straight and turn left.', 'Where is the bus stop?', 'Go straight and turn left.', 'beginner'),
        ('daily', 'At the doctor', 'Doctor, I have a fever.', 'Do not worry. Take this medicine.', 'Doctor, I have a fever.', 'Do not worry. Take this medicine.', 'intermediate'),
        ('office', 'Good morning', 'Good morning sir.', 'Hello, how are you?', 'Good morning sir.', 'Hello, how are you?', 'beginner'),
        ('office', 'Meeting time', 'What time is the meeting?', 'The meeting is at 3 o\'clock.', 'What time is the meeting?', 'The meeting is at 3 o\'clock.', 'intermediate'),
        ('office', 'Asking for leave', 'Sir, can I take leave tomorrow?', 'Okay, you may go.', 'Sir, can I take leave tomorrow?', 'Okay, you may go.', 'intermediate'),
        ('interview', 'Self introduction', 'My name is Jayan. I studied CS.', 'Good. Do you have experience?', 'My name is Jayan. I studied CS.', 'Good. Do you have experience?', 'intermediate'),
        ('interview', 'Strengths', 'My strength is hard work.', 'Good. What is your weakness?', 'My strength is hard work.', 'Good. What is your weakness?', 'intermediate'),
        ('family', 'Introducing family', 'This is my mother. She is a teacher.', 'Hello madam. Your son is talented.', 'This is my mother. She is a teacher.', 'Hello madam. Your son is talented.', 'beginner'),
        ('family', 'Dinner', 'Mom, what did you cook today?', 'I cooked sambar rice.', 'Mom, what did you cook today?', 'I cooked sambar rice.', 'beginner'),
    ]
    cur.executemany(
        'INSERT INTO dialogue_templates (scenario, title, speaker_a, speaker_b, english_a, english_b, difficulty) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        dialogues
    )

    print("Seeding badges...")
    badges = [
        ('First Sentence', 'Generated your first Tamil sentence!', 'star', 1),
        ('Word Saver', 'Saved 5 sentences to your collection.', 'save', 5),
        ('Tamil Talker', 'Used the AI Tutor 10 times.', 'chat', 10),
        ('Quiz Starter', 'Completed your first quiz!', 'quiz', 1),
        ('High Scorer', 'Scored 100 points in a quiz.', 'trophy', 100),
        ('Daily Learner', 'Maintained a 3-day learning streak.', 'fire', 3),
        ('Grammar Guru', 'Checked grammar 5 times.', 'check', 5),
        ('Dialogue Master', 'Practiced 10 dialogues.', 'speak', 10),
    ]
    cur.executemany(
        'INSERT INTO badges (name, description, icon, threshold) VALUES (%s, %s, %s, %s)',
        badges
    )

    print("Seeding initial user_points row...")
    cur.execute(
        'INSERT INTO user_points (total_points, streak_days, last_active) VALUES (%s, %s, %s)',
        (0, 0, str(date.today()))
    )

    db.commit()
    db.close()
    print("\nSUCCESS: Supabase PostgreSQL database successfully created and seeded!")
    print("Tables: vocabulary, grammar_rules, saved_sentences,")
    print("        dialogue_templates, quiz_results, user_points, badges, user_badges")


if __name__ == '__main__':
    init_database()
