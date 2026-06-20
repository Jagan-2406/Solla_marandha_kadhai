# backend/db_manager.py
# Database helper — all PostgreSQL (Supabase) read/write functions

import psycopg2
import psycopg2.extras
import os
from datetime import date, datetime

# Get DATABASE_URL from environment (set in Render dashboard)
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Supabase sometimes provides 'postgres://' — psycopg2 needs 'postgresql://'
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


def conn():
    """Open and return a PostgreSQL connection."""
    connection = psycopg2.connect(DATABASE_URL)
    return connection


def _fetchall(cursor):
    """Convert RealDictRow results to plain dicts."""
    return [dict(row) for row in cursor.fetchall()]


def _fetchone(cursor):
    """Convert a single RealDictRow to a plain dict, or None."""
    row = cursor.fetchone()
    return dict(row) if row else None


# ─────────────────────────────────────────────────────────
# Phase 2: Vocabulary
# ─────────────────────────────────────────────────────────

def get_all_vocabulary():
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM vocabulary ORDER BY category, tamil_word')
        return _fetchall(cur)
    finally:
        db.close()


def search_vocabulary(q):
    db = conn()
    try:
        query = f'%{q}%'
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            'SELECT * FROM vocabulary WHERE tamil_word LIKE %s OR english_meaning LIKE %s ORDER BY category',
            (query, query)
        )
        return _fetchall(cur)
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# Phase 2: Grammar Rules
# ─────────────────────────────────────────────────────────

def get_suffix(tense, gender):
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            'SELECT suffix FROM grammar_rules WHERE tense=%s AND gender=%s LIMIT 1',
            (tense, gender)
        )
        r = _fetchone(cur)
        return r['suffix'] if r else 'கிறேன்'
    finally:
        db.close()


def get_subject(gender):
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            'SELECT subject FROM grammar_rules WHERE gender=%s LIMIT 1',
            (gender,)
        )
        r = _fetchone(cur)
        return r['subject'] if r else 'நான்'
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# Phase 2: Saved Sentences
# ─────────────────────────────────────────────────────────

def save_sentence(sentence, stype, tense):
    db = conn()
    try:
        cur = db.cursor()
        cur.execute(
            'INSERT INTO saved_sentences (sentence, sentence_type, tense) VALUES (%s, %s, %s)',
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
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM saved_sentences ORDER BY saved_at DESC')
        return _fetchall(cur)
    finally:
        db.close()


def delete_saved(sid):
    db = conn()
    try:
        cur = db.cursor()
        cur.execute('DELETE FROM saved_sentences WHERE id=%s', (sid,))
        db.commit()
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G2: Dialogue Library
# ─────────────────────────────────────────────────────────

def get_dialogues(scenario=''):
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if scenario and scenario != 'all':
            cur.execute(
                'SELECT * FROM dialogue_templates WHERE scenario=%s ORDER BY difficulty, id',
                (scenario,)
            )
        else:
            cur.execute(
                'SELECT * FROM dialogue_templates ORDER BY scenario, difficulty, id'
            )
        return _fetchall(cur)
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G3: Daily Word
# ─────────────────────────────────────────────────────────

def get_daily_word():
    db = conn()
    try:
        today_seed = int(date.today().strftime('%j'))  # day of year
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM vocabulary')
        rows = _fetchall(cur)
        if not rows:
            return {}
        idx = today_seed % len(rows)
        return rows[idx]
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G4: Quiz Results
# ─────────────────────────────────────────────────────────

def save_quiz_result(quiz_type, score, total):
    db = conn()
    try:
        cur = db.cursor()
        cur.execute(
            'INSERT INTO quiz_results (quiz_type, score, total) VALUES (%s, %s, %s)',
            (quiz_type, score, total)
        )
        db.commit()
        award_points(score * 20)
        if score == total and total > 0:
            award_points(50)  # bonus for perfect quiz
    finally:
        db.close()


def get_quiz_history(limit=10):
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            'SELECT * FROM quiz_results ORDER BY taken_at DESC LIMIT %s',
            (limit,)
        )
        return _fetchall(cur)
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G5: Gamification — Points, Streak, Badges
# ─────────────────────────────────────────────────────────

def _ensure_user_points():
    """Ensure the single user_points row exists."""
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT id FROM user_points LIMIT 1')
        row = _fetchone(cur)
        if not row:
            cur2 = db.cursor()
            cur2.execute(
                'INSERT INTO user_points (total_points, streak_days, last_active) VALUES (0, 0, %s)',
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
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM user_points LIMIT 1')
        row = _fetchone(cur)
        if not row:
            return

        today = str(date.today())
        last = str(row['last_active']) if row['last_active'] else ''
        streak = row['streak_days'] or 0
        new_points = (row['total_points'] or 0) + amount

        # Streak logic
        if last == today:
            new_streak = streak
        else:
            try:
                last_date = datetime.strptime(last[:10], '%Y-%m-%d').date() if last else None
                delta = (date.today() - last_date).days if last_date else 999
                new_streak = streak + 1 if delta == 1 else (1 if delta > 1 else streak)
            except Exception:
                new_streak = 1

        cur2 = db.cursor()
        cur2.execute(
            'UPDATE user_points SET total_points=%s, streak_days=%s, last_active=%s',
            (new_points, new_streak, today)
        )
        db.commit()

        # Check badge milestones
        _check_badges(new_points, new_streak, db)
    finally:
        db.close()


def _check_badges(points, streak, db):
    """Award badges automatically based on milestones."""
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT badge_id FROM user_badges')
    earned_ids = {r['badge_id'] for r in _fetchall(cur)}

    cur.execute('SELECT * FROM badges')
    badges = _fetchall(cur)

    cur2 = db.cursor()
    for badge in badges:
        bid = badge['id']
        if bid in earned_ids:
            continue
        if badge['name'] == 'Daily Learner' and streak >= badge['threshold']:
            cur2.execute('INSERT INTO user_badges (badge_id) VALUES (%s)', (bid,))
        elif badge['name'] == 'High Scorer' and points >= badge['threshold']:
            cur2.execute('INSERT INTO user_badges (badge_id) VALUES (%s)', (bid,))
    db.commit()


def get_dashboard_stats():
    """Fetch all stats for the dashboard page."""
    _ensure_user_points()
    db = conn()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute('SELECT * FROM user_points LIMIT 1')
        points_row = _fetchone(cur)
        total_points = points_row['total_points'] if points_row else 0
        streak_days  = points_row['streak_days'] if points_row else 0

        cur.execute('SELECT COUNT(*) AS cnt FROM saved_sentences')
        saved_count = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) AS cnt FROM quiz_results')
        quiz_count = cur.fetchone()[0]

        cur.execute(
            'SELECT AVG(CAST(score AS REAL)/total*100) FROM quiz_results WHERE total>0'
        )
        avg_row = cur.fetchone()
        avg_score = round(avg_row[0] or 0, 1) if avg_row else 0

        cur2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur2.execute('''
            SELECT b.name, b.description, b.icon, ub.earned_at
            FROM user_badges ub JOIN badges b ON ub.badge_id = b.id
            ORDER BY ub.earned_at DESC
        ''')
        earned_badges = _fetchall(cur2)

        cur2.execute('SELECT * FROM quiz_results ORDER BY taken_at DESC LIMIT 5')
        quiz_history = _fetchall(cur2)

        return {
            'total_points': total_points,
            'streak_days':  streak_days,
            'saved_count':  saved_count,
            'quiz_count':   quiz_count,
            'avg_score':    avg_score,
            'badges':       earned_badges,
            'quiz_history': quiz_history,
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
