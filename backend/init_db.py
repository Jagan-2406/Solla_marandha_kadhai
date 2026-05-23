# backend/init_db.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'tamil_nlp.db')

def init_database():
    # If DB already exists, we delete it to start fresh and avoid constraints issues
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database deleted. Re-initializing...")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create vocabulary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tamil_word TEXT NOT NULL,
            english_meaning TEXT NOT NULL,
            category TEXT NOT NULL,
            gender_class TEXT
        )
    ''')
    
    # Create grammar_rules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grammar_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tense TEXT NOT NULL,
            gender TEXT NOT NULL,
            suffix TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    ''')
    
    # Create saved_sentences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT NOT NULL,
            sentence_type TEXT NOT NULL,
            tense TEXT NOT NULL,
            saved_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Starter vocabulary data
    vocab_items = [
        # Nouns
        ('பால்', 'milk', 'noun', 'neutral'),
        ('சோறு', 'rice', 'noun', 'neutral'),
        ('தண்ணீர்', 'water', 'noun', 'neutral'),
        ('புத்தகம்', 'book', 'noun', 'neutral'),
        ('பள்ளி', 'school', 'noun', 'neutral'),
        ('வீடு', 'house', 'noun', 'neutral'),
        ('பாடம்', 'lesson', 'noun', 'neutral'),
        ('பாடல்', 'song', 'noun', 'neutral'),
        ('திரைப்படம்', 'movie', 'noun', 'neutral'),
        ('விளையாட்டு', 'game', 'noun', 'neutral'),
        # Verbs
        ('குடி', 'drink', 'verb', 'neutral'),
        ('சாப்பிடு', 'eat', 'verb', 'neutral'),
        ('படி', 'study', 'verb', 'neutral'),
        ('எழுது', 'write', 'verb', 'neutral'),
        ('பாடு', 'sing', 'verb', 'neutral'),
        ('விளையாடு', 'play', 'verb', 'neutral'),
        ('ஓடு', 'run', 'verb', 'neutral'),
        ('பேசு', 'speak', 'verb', 'neutral'),
        ('பார்', 'see', 'verb', 'neutral'),
        ('போ', 'go', 'verb', 'neutral'),
        ('வா', 'come', 'verb', 'neutral')
    ]
    cursor.executemany(
        'INSERT INTO vocabulary (tamil_word, english_meaning, category, gender_class) VALUES (?, ?, ?, ?)',
        vocab_items
    )
    
    # Starter grammar rules (tense, gender/person, suffix, subject pronoun)
    # The suffix here is the combination of tense marker + pronominal ending for simple rules,
    # and we will store the correct subjects as well.
    rules = [
        # Present tense
        ('present', 'first', 'கிறேன்', 'நான்'),
        ('present', 'male', 'கிறான்', 'அவன்'),
        ('present', 'female', 'கிறாள்', 'அவள்'),
        ('present', 'neutral', 'கிறது', 'அது'),
        ('present', 'plural', 'கிறார்கள்', 'அவர்கள்'),
        
        # Past tense
        ('past', 'first', 'னேன்', 'நான்'),
        ('past', 'male', 'னான்', 'அவன்'),
        ('past', 'female', 'னாள்', 'அவள்'),
        ('past', 'neutral', 'னது', 'அது'),
        ('past', 'plural', 'னார்கள்', 'அவர்கள்'),
        
        # Future tense
        ('future', 'first', 'வேன்', 'நான்'),
        ('future', 'male', 'வான்', 'அவன்'),
        ('future', 'female', 'வாள்', 'அவள்'),
        ('future', 'neutral', 'கும்', 'அது'),
        ('future', 'plural', 'வார்கள்', 'அவர்கள்'),
    ]
    cursor.executemany(
        'INSERT INTO grammar_rules (tense, gender, suffix, subject) VALUES (?, ?, ?, ?)',
        rules
    )
    
    conn.commit()
    conn.close()
    print("SQLite database successfully created and seeded: backend/tamil_nlp.db")

if __name__ == '__main__':
    init_database()
