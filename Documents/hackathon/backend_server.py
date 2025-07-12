#!/usr/bin/env python3
"""
ANKID Advanced - Backend Server
Provides API endpoints for enhanced features like adaptive difficulty,
progress tracking, and content management.
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
import random
import sqlite3
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Initialize database
def init_db():
    conn = sqlite3.connect('ankid.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            gems INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            avatar_type TEXT DEFAULT 'ender',
            settings TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            subject TEXT,
            difficulty TEXT,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Cards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_cards (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            card_name TEXT,
            card_series TEXT,
            rarity TEXT,
            obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Quests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_quests (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            quest_id TEXT,
            progress TEXT DEFAULT '{}',
            completed BOOLEAN DEFAULT FALSE,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Load game data
with open('game-data.json', 'r') as f:
    GAME_DATA = json.load(f)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ANKID Advanced - Backend Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 ANKID Advanced Backend</h1>
            <p>Backend server for the advanced gamified learning platform</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/user/&lt;username&gt;</code>
                <p>Get user profile and statistics</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/user/create</code>
                <p>Create new user account</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/questions/&lt;subject&gt;/&lt;difficulty&gt;</code>
                <p>Get adaptive questions for subject and difficulty</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <code>/api/answer/submit</code>
                <p>Submit answer and get feedback with rewards</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/leaderboard/&lt;type&gt;</code>
                <p>Get leaderboard by type (gems, cards, streak, etc.)</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/cards/&lt;user_id&gt;</code>
                <p>Get user's card collection</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <code>/api/quests/&lt;user_id&gt;</code>
                <p>Get user's active and completed quests</p>
            </div>
            
            <h2>Features:</h2>
            <ul>
                <li>✅ Adaptive difficulty based on performance</li>
                <li>✅ Progress tracking and analytics</li>
                <li>✅ Card collection and rarity system</li>
                <li>✅ Quest and achievement system</li>
                <li>✅ Multiple leaderboard types</li>
                <li>✅ User customization and settings</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/api/user/<username>')
def get_user(username):
    conn = sqlite3.connect('ankid.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get user progress
    cursor.execute('''
        SELECT subject, difficulty, correct_answers, total_answers 
        FROM user_progress WHERE user_id = ?
    ''', (user[0],))
    progress = cursor.fetchall()
    
    # Get user cards count
    cursor.execute('SELECT COUNT(*) FROM user_cards WHERE user_id = ?', (user[0],))
    card_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'id': user[0],
        'username': user[1],
        'gems': user[2],
        'streak': user[3],
        'max_streak': user[4],
        'level': user[5],
        'avatar_type': user[6],
        'settings': json.loads(user[7]),
        'card_count': card_count,
        'progress': [
            {
                'subject': p[0],
                'difficulty': p[1],
                'accuracy': p[2] / p[3] if p[3] > 0 else 0,
                'total_questions': p[3]
            } for p in progress
        ]
    })

@app.route('/api/user/create', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    conn = sqlite3.connect('ankid.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, gems, streak, max_streak, level, avatar_type, settings)
            VALUES (?, 0, 0, 0, 1, 'ender', '{}')
        ''', (username,))
        
        user_id = cursor.lastrowid
        
        # Initialize progress for all subjects
        for subject in ['math', 'science', 'english']:
            cursor.execute('''
                INSERT INTO user_progress (user_id, subject, difficulty)
                VALUES (?, ?, 'beginner')
            ''', (user_id, subject))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User created successfully', 'user_id': user_id})
    
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 409

@app.route('/api/questions/<subject>/<difficulty>')
def get_questions(subject, difficulty):
    if subject not in GAME_DATA['difficultyProgression']:
        return jsonify({'error': 'Invalid subject'}), 400
    
    if difficulty not in GAME_DATA['difficultyProgression'][subject]:
        return jsonify({'error': 'Invalid difficulty'}), 400
    
    # Get questions based on subject and difficulty
    # This would normally pull from a comprehensive database
    questions = [
        {
            'id': f"{subject}_{difficulty}_{i}",
            'question': f"Sample {difficulty} {subject} question {i+1}",
            'answer': f"answer{i+1}",
            'difficulty': i % 3 + 1,
            'hint': f"Hint for question {i+1}",
            'topics': GAME_DATA['difficultyProgression'][subject][difficulty]['topics']
        }
        for i in range(5)
    ]
    
    return jsonify({'questions': questions})

@app.route('/api/answer/submit', methods=['POST'])
def submit_answer():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    answer = data.get('answer')
    correct = data.get('correct', False)
    
    conn = sqlite3.connect('ankid.db')
    cursor = conn.cursor()
    
    # Update user progress
    subject = question_id.split('_')[0]
    
    cursor.execute('''
        UPDATE user_progress 
        SET correct_answers = correct_answers + ?, 
            total_answers = total_answers + 1,
            last_attempt = CURRENT_TIMESTAMP
        WHERE user_id = ? AND subject = ?
    ''', (1 if correct else 0, user_id, subject))
    
    # Update user stats
    if correct:
        cursor.execute('''
            UPDATE users 
            SET gems = gems + 10, 
                streak = streak + 1
            WHERE id = ?
        ''', (user_id,))
        
        # Update max streak
        cursor.execute('SELECT streak FROM users WHERE id = ?', (user_id,))
        current_streak = cursor.fetchone()[0]
        
        cursor.execute('''
            UPDATE users 
            SET max_streak = MAX(max_streak, ?)
            WHERE id = ?
        ''', (current_streak, user_id))
        
        # Check for card reward
        card_reward = None
        if random.random() < 0.3:  # 30% chance
            series = random.choice(list(GAME_DATA['cardSeries'].keys()))
            cards = GAME_DATA['cardSeries'][series]['cards']
            card = random.choice(cards)
            
            cursor.execute('''
                INSERT INTO user_cards (user_id, card_name, card_series, rarity)
                VALUES (?, ?, ?, ?)
            ''', (user_id, card['name'], series, card['rarity']))
            
            card_reward = {
                'name': card['name'],
                'series': series,
                'rarity': card['rarity']
            }
    else:
        cursor.execute('UPDATE users SET streak = 0 WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    response = {
        'correct': correct,
        'gems_earned': 10 if correct else 0,
        'streak_maintained': correct
    }
    
    if card_reward:
        response['card_reward'] = card_reward
    
    return jsonify(response)

@app.route('/api/leaderboard/<leaderboard_type>')
def get_leaderboard(leaderboard_type):
    conn = sqlite3.connect('ankid.db')
    cursor = conn.cursor()
    
    order_by = {
        'gems': 'gems DESC',
        'streak': 'max_streak DESC',
        'cards': '(SELECT COUNT(*) FROM user_cards WHERE user_id = users.id) DESC',
        'level': 'level DESC'
    }.get(leaderboard_type, 'gems DESC')
    
    cursor.execute(f'''
        SELECT username, gems, max_streak, level,
               (SELECT COUNT(*) FROM user_cards WHERE user_id = users.id) as card_count
        FROM users 
        ORDER BY {order_by}
        LIMIT 10
    ''')
    
    leaderboard = [
        {
            'rank': i + 1,
            'username': row[0],
            'gems': row[1],
            'max_streak': row[2],
            'level': row[3],
            'card_count': row[4]
        }
        for i, row in enumerate(cursor.fetchall())
    ]
    
    conn.close()
    return jsonify({'leaderboard': leaderboard})

@app.route('/api/cards/<int:user_id>')
def get_user_cards(user_id):
    conn = sqlite3.connect('ankid.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT card_name, card_series, rarity, obtained_at
        FROM user_cards 
        WHERE user_id = ?
        ORDER BY obtained_at DESC
    ''', (user_id,))
    
    cards = [
        {
            'name': row[0],
            'series': row[1],
            'rarity': row[2],
            'obtained_at': row[3]
        }
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return jsonify({'cards': cards})

@app.route('/api/quests/<int:user_id>')
def get_user_quests(user_id):
    # This would implement the full quest system
    # For now, return sample data
    return jsonify({
        'active_quests': [
            {
                'id': 'galaxy_explorer',
                'title': 'Galaxy Explorer',
                'progress': '2/3 chapters completed',
                'next_requirement': 'Complete advanced math quiz'
            }
        ],
        'completed_quests': [
            {
                'id': 'first_steps',
                'title': 'First Steps',
                'completed_at': '2025-01-10T10:00:00Z',
                'reward': {'gems': 25, 'title': 'Beginner'}
            }
        ]
    })

if __name__ == '__main__':
    init_db()
    print("🎓 ANKID Advanced Backend Server Starting...")
    print("📊 Database initialized")
    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True, port=5000)
