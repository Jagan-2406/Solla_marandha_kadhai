# backend/db_manager.py
# Database helper — all SQLite read/write functions

import sqlite3
import os
from datetime import date, datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'tamil_nlp.db')


def conn():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ─────────────────────────────────────────────────────────
# Phase 2: Vocabulary
# ─────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────
# Phase 2: Grammar Rules
# ─────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────
# Phase 2: Saved Sentences
# ─────────────────────────────────────────────────────────

def save_sentence(sentence, stype, tense):
    db = conn()
    try:
        db.execute(
            'INSERT INTO saved_sentences (sentence, sentence_type, tense) VALUES (?, ?, ?)',
            (sentence, stype, tense)
        )
        db.commit()
        # Award points for saving
        award_points(10)
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


# ─────────────────────────────────────────────────────────
# G2: Dialogue Library
# ─────────────────────────────────────────────────────────

def get_dialogues(scenario=''):
    db = conn()
    try:
        if scenario and scenario != 'all':
            rows = db.execute(
                'SELECT * FROM dialogue_templates WHERE scenario=? ORDER BY difficulty, id',
                (scenario,)
            ).fetchall()
        else:
            rows = db.execute(
                'SELECT * FROM dialogue_templates ORDER BY scenario, difficulty, id'
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G3: Daily Word
# ─────────────────────────────────────────────────────────

def get_daily_word():
    db = conn()
    try:
        # Use date as seed for consistent "word of the day"
        today_seed = int(date.today().strftime('%j'))  # day of year
        rows = db.execute('SELECT * FROM vocabulary').fetchall()
        if not rows:
            return {}
        idx = today_seed % len(rows)
        return dict(rows[idx])
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G4: Quiz Results
# ─────────────────────────────────────────────────────────

def save_quiz_result(quiz_type, score, total):
    db = conn()
    try:
        db.execute(
            'INSERT INTO quiz_results (quiz_type, score, total) VALUES (?, ?, ?)',
            (quiz_type, score, total)
        )
        db.commit()
        # Award points per correct answer
        award_points(score * 20)
        # Check if perfect score → extra badge milestone
        if score == total and total > 0:
            award_points(50)  # bonus for perfect quiz
    finally:
        db.close()


def get_quiz_history(limit=10):
    db = conn()
    try:
        rows = db.execute(
            'SELECT * FROM quiz_results ORDER BY taken_at DESC LIMIT ?',
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G5: Gamification — Points, Streak, Badges
# ─────────────────────────────────────────────────────────

def _ensure_user_points():
    """Ensure the single user_points row exists."""
    db = conn()
    try:
        row = db.execute('SELECT id FROM user_points LIMIT 1').fetchone()
        if not row:
            db.execute(
                'INSERT INTO user_points (total_points, streak_days, last_active) VALUES (0, 0, ?)',
                (str(date.today()),)
            )
            db.commit()
    finally:
        db.close()


def award_points(amount):
    """Add points to the user and update streak."""
    _ensure_user_points()
    db = conn()
    try:
        row = db.execute('SELECT * FROM user_points LIMIT 1').fetchone()
        if not row:
            return

        today = str(date.today())
        last = str(row['last_active']) if row['last_active'] else ''
        streak = row['streak_days'] or 0
        new_points = (row['total_points'] or 0) + amount

        # Streak logic: if last active was yesterday → increment; today → keep; else reset
        if last == today:
            new_streak = streak
        else:
            try:
                last_date = datetime.strptime(last, '%Y-%m-%d').date() if last else None
                delta = (date.today() - last_date).days if last_date else 999
                new_streak = streak + 1 if delta == 1 else (1 if delta > 1 else streak)
            except Exception:
                new_streak = 1

        db.execute(
            'UPDATE user_points SET total_points=?, streak_days=?, last_active=?',
            (new_points, new_streak, today)
        )
        db.commit()

        # Automatically award badge milestones
        _check_badges(new_points, new_streak, db)
    finally:
        db.close()


def _check_badges(points, streak, db):
    """Award badges automatically based on milestones."""
    earned_ids = {r['badge_id'] for r in db.execute('SELECT badge_id FROM user_badges').fetchall()}
    badges = db.execute('SELECT * FROM badges').fetchall()
    for badge in badges:
        bid = badge['id']
        if bid in earned_ids:
            continue
        # Use threshold for different badge types
        if badge['name'] == 'Daily Learner' and streak >= badge['threshold']:
            db.execute('INSERT INTO user_badges (badge_id) VALUES (?)', (bid,))
        elif badge['name'] == 'High Scorer' and points >= badge['threshold']:
            db.execute('INSERT INTO user_badges (badge_id) VALUES (?)', (bid,))
    db.commit()


def get_dashboard_stats():
    """Fetch all stats for the dashboard page."""
    _ensure_user_points()
    db = conn()
    try:
        points_row = db.execute('SELECT * FROM user_points LIMIT 1').fetchone()
        total_points = points_row['total_points'] if points_row else 0
        streak_days  = points_row['streak_days'] if points_row else 0

        saved_count = db.execute('SELECT COUNT(*) FROM saved_sentences').fetchone()[0]
        quiz_count  = db.execute('SELECT COUNT(*) FROM quiz_results').fetchone()[0]
        avg_score_row = db.execute(
            'SELECT AVG(CAST(score AS REAL)/total*100) FROM quiz_results WHERE total>0'
        ).fetchone()
        avg_score = round(avg_score_row[0] or 0, 1)

        # Badge list
        earned_badges = db.execute('''
            SELECT b.name, b.description, b.icon, ub.earned_at
            FROM user_badges ub JOIN badges b ON ub.badge_id = b.id
            ORDER BY ub.earned_at DESC
        ''').fetchall()

        # Recent quiz results
        quiz_history = db.execute(
            'SELECT * FROM quiz_results ORDER BY taken_at DESC LIMIT 5'
        ).fetchall()

        return {
            'total_points': total_points,
            'streak_days':  streak_days,
            'saved_count':  saved_count,
            'quiz_count':   quiz_count,
            'avg_score':    avg_score,
            'badges':       [dict(b) for b in earned_badges],
            'quiz_history': [dict(q) for q in quiz_history],
        }
    finally:
        db.close()


def award_action_points(action):
    """Award points based on a named action type."""
    point_map = {
        'generate': 5,
        'save': 10,
        'grammar_check': 15,
        'dialogue_practice': 10,
        'quiz_complete': 20,
    }
    amount = point_map.get(action, 5)
    award_points(amount)
