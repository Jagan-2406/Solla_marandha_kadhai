# backend/db_manager.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'tamil_nlp.db')

def conn():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def get_all_vocabulary():
    db = conn()
    try:
        rows = db.execute('SELECT * FROM vocabulary ORDER BY category, tamil_word').fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()

def search_vocabulary(q):
    db = conn()
    try:
        query = f'%{q}%'
        rows = db.execute(
            'SELECT * FROM vocabulary WHERE tamil_word LIKE ? OR english_meaning LIKE ? ORDER BY category',
            (query, query)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()

def get_suffix(tense, gender):
    db = conn()
    try:
        r = db.execute(
            'SELECT suffix FROM grammar_rules WHERE tense=? AND gender=? LIMIT 1',
            (tense, gender)
        ).fetchone()
        return r['suffix'] if r else 'கிறேன்'
    finally:
        db.close()

def get_subject(gender):
    db = conn()
    try:
        r = db.execute(
            'SELECT subject FROM grammar_rules WHERE gender=? LIMIT 1',
            (gender,)
        ).fetchone()
        return r['subject'] if r else 'நான்'
    finally:
        db.close()

def save_sentence(sentence, stype, tense):
    db = conn()
    try:
        db.execute(
            'INSERT INTO saved_sentences (sentence, sentence_type, tense) VALUES (?, ?, ?)',
            (sentence, stype, tense)
        )
        db.commit()
    finally:
        db.close()

def get_saved():
    db = conn()
    try:
        rows = db.execute('SELECT * FROM saved_sentences ORDER BY saved_at DESC').fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()

def delete_saved(sid):
    db = conn()
    try:
        db.execute('DELETE FROM saved_sentences WHERE id=?', (sid,))
        db.commit()
    finally:
        db.close()
