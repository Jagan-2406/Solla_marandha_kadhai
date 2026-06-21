# backend/db_manager.py
# Database helper — PostgreSQL (Supabase) using pg8000 DB-API interface

import pg8000
import os
from datetime import date, datetime
from urllib.parse import urlparse, unquote

# Get DATABASE_URL from environment (set in Render dashboard or backend/.env)
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


def _parse_url(url):
    """Parse a PostgreSQL URL into connection kwargs."""
    p = urlparse(url)
    return {
        'host':     p.hostname,
        'port':     p.port or 5432,
        'database': p.path.lstrip('/'),
        'user':     unquote(p.username or ''),
        'password': unquote(p.password or ''),
        'ssl_context': True,
    }


def conn():
    """Open and return a pg8000 DB-API connection."""
    return pg8000.connect(**_parse_url(DATABASE_URL))


# ─────────────────────────────────────────────────────────
# Phase 2: Vocabulary
# ─────────────────────────────────────────────────────────

def get_all_vocabulary():
    db = conn()
    try:
        cur = db.cursor()
        cur.execute('SELECT * FROM vocabulary ORDER BY category, tamil_word')
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        db.close()


def search_vocabulary(q):
    db = conn()
    try:
        query = f'%{q}%'
        cur = db.cursor()
        cur.execute(
            'SELECT * FROM vocabulary WHERE tamil_word LIKE %s OR english_meaning LIKE %s ORDER BY category',
            (query, query)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# Phase 2: Grammar Rules
# ─────────────────────────────────────────────────────────

def get_suffix(tense, gender):
    db = conn()
    try:
        cur = db.cursor()
        cur.execute(
            'SELECT suffix FROM grammar_rules WHERE tense=%s AND gender=%s LIMIT 1',
            (tense, gender)
        )
        row = cur.fetchone()
        return row[0] if row else 'கிறேன்'
    finally:
        db.close()


def get_subject(gender):
    db = conn()
    try:
        cur = db.cursor()
        cur.execute(
            'SELECT subject FROM grammar_rules WHERE gender=%s LIMIT 1',
            (gender,)
        )
        row = cur.fetchone()
        return row[0] if row else 'நான்'
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
        award_points(10)
    finally:
        db.close()


def get_saved():
    db = conn()
    try:
        cur = db.cursor()
        cur.execute('SELECT * FROM saved_sentences ORDER BY saved_at DESC')
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
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
        cur = db.cursor()
        if scenario and scenario != 'all':
            cur.execute(
                'SELECT * FROM dialogue_templates WHERE scenario=%s ORDER BY difficulty, id',
                (scenario,)
            )
        else:
            cur.execute(
                'SELECT * FROM dialogue_templates ORDER BY scenario, difficulty, id'
            )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G3: Daily Word
# ─────────────────────────────────────────────────────────

def get_daily_word():
    db = conn()
    try:
        today_seed = int(date.today().strftime('%j'))
        cur = db.cursor()
        cur.execute('SELECT * FROM vocabulary')
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        if not rows:
            return {}
        return rows[today_seed % len(rows)]
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
            award_points(50)
    finally:
        db.close()


def get_quiz_history(limit=10):
    db = conn()
    try:
        cur = db.cursor()
        cur.execute(
            'SELECT * FROM quiz_results ORDER BY taken_at DESC LIMIT %s',
            (limit,)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        db.close()


# ─────────────────────────────────────────────────────────
# G5: Gamification — Points, Streak, Badges
# ─────────────────────────────────────────────────────────

def _ensure_user_points():
    db = conn()
    try:
        cur = db.cursor()
        cur.execute('SELECT id FROM user_points LIMIT 1')
        if not cur.fetchone():
            cur.execute(
                'INSERT INTO user_points (total_points, streak_days, last_active) VALUES (%s, %s, %s)',
                (0, 0, str(date.today()))
            )
            db.commit()
    finally:
        db.close()


def award_points(amount):
    _ensure_user_points()
    db = conn()
    try:
        cur = db.cursor()
        cur.execute('SELECT * FROM user_points LIMIT 1')
        cols = [d[0] for d in cur.description]
        row_raw = cur.fetchone()
        if not row_raw:
            return
        row = dict(zip(cols, row_raw))

        today = str(date.today())
        last = str(row['last_active'])[:10] if row['last_active'] else ''
        streak = row['streak_days'] or 0
        new_points = (row['total_points'] or 0) + amount

        if last == today:
            new_streak = streak
        else:
            try:
                last_date = datetime.strptime(last, '%Y-%m-%d').date() if last else None
                delta = (date.today() - last_date).days if last_date else 999
                new_streak = streak + 1 if delta == 1 else (1 if delta > 1 else streak)
            except Exception:
                new_streak = 1

        cur.execute(
            'UPDATE user_points SET total_points=%s, streak_days=%s, last_active=%s',
            (new_points, new_streak, today)
        )
        db.commit()
        _check_badges(new_points, new_streak, db)
    finally:
        db.close()


def _check_badges(points, streak, db):
    cur = db.cursor()
    cur.execute('SELECT badge_id FROM user_badges')
    earned_ids = {row[0] for row in cur.fetchall()}

    cur.execute('SELECT * FROM badges')
    cols = [d[0] for d in cur.description]
    badges = [dict(zip(cols, row)) for row in cur.fetchall()]

    for badge in badges:
        bid = badge['id']
        if bid in earned_ids:
            continue
        if badge['name'] == 'Daily Learner' and streak >= badge['threshold']:
            cur.execute('INSERT INTO user_badges (badge_id) VALUES (%s)', (bid,))
        elif badge['name'] == 'High Scorer' and points >= badge['threshold']:
            cur.execute('INSERT INTO user_badges (badge_id) VALUES (%s)', (bid,))
    db.commit()


def get_dashboard_stats():
    _ensure_user_points()
    db = conn()
    try:
        cur = db.cursor()

        cur.execute('SELECT * FROM user_points LIMIT 1')
        cols = [d[0] for d in cur.description]
        pr = cur.fetchone()
        points_row = dict(zip(cols, pr)) if pr else {}
        total_points = points_row.get('total_points', 0)
        streak_days  = points_row.get('streak_days', 0)

        cur.execute('SELECT COUNT(*) FROM saved_sentences')
        saved_count = cur.fetchone()[0]

        cur.execute('SELECT COUNT(*) FROM quiz_results')
        quiz_count = cur.fetchone()[0]

        cur.execute('SELECT AVG(CAST(score AS REAL)/total*100) FROM quiz_results WHERE total>0')
        avg_row = cur.fetchone()
        avg_score = round((avg_row[0] or 0), 1) if avg_row else 0

        cur.execute('''
            SELECT b.name, b.description, b.icon, ub.earned_at
            FROM user_badges ub JOIN badges b ON ub.badge_id = b.id
            ORDER BY ub.earned_at DESC
        ''')
        badge_cols = [d[0] for d in cur.description]
        earned_badges = [dict(zip(badge_cols, row)) for row in cur.fetchall()]

        cur.execute('SELECT * FROM quiz_results ORDER BY taken_at DESC LIMIT 5')
        qh_cols = [d[0] for d in cur.description]
        quiz_history = [dict(zip(qh_cols, row)) for row in cur.fetchall()]

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
    point_map = {
        'generate': 5,
        'save': 10,
        'grammar_check': 15,
        'dialogue_practice': 10,
        'quiz_complete': 20,
    }
    award_points(point_map.get(action, 5))
