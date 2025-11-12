"""
User API Service
A simple Flask REST API for user management
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*'))

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///users.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SECRET_KEY'] = SECRET_KEY

# Database initialization
def init_db():
    """Initialize the database with users table"""
    db_path = DATABASE_URL.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert sample data if table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ('john_doe', 'john@example.com', 'John Doe'),
            ('jane_smith', 'jane@example.com', 'Jane Smith'),
            ('bob_wilson', 'bob@example.com', 'Bob Wilson'),
        ]
        cursor.executemany(
            'INSERT INTO users (username, email, full_name) VALUES (?, ?, ?)',
            sample_users
        )
        logger.info("Inserted sample users")

    conn.commit()
    conn.close()
    logger.info("Database initialized")

def get_db_connection():
    """Get database connection"""
    db_path = DATABASE_URL.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Routes

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-api',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()

        users_list = [
            {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'created_at': user['created_at'],
                'updated_at': user['updated_at']
            }
            for user in users
        ]

        return jsonify({
            'success': True,
            'count': len(users_list),
            'users': users_list
        }), 200

    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch users'
        }), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'created_at': user['created_at'],
                'updated_at': user['updated_at']
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user'
        }), 500

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not data.get('username') or not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Username and email are required'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (username, email, full_name)
            VALUES (?, ?, ?)
        ''', (
            data['username'],
            data['email'],
            data.get('full_name', '')
        ))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Created user: {data['username']} (ID: {user_id})")

        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': user_id
        }), 201

    except sqlite3.IntegrityError as e:
        logger.warning(f"Duplicate user creation attempt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Username or email already exists'
        }), 409

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create user'
        }), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Update user
        update_fields = []
        update_values = []

        if 'username' in data:
            update_fields.append('username = ?')
            update_values.append(data['username'])

        if 'email' in data:
            update_fields.append('email = ?')
            update_values.append(data['email'])

        if 'full_name' in data:
            update_fields.append('full_name = ?')
            update_values.append(data['full_name'])

        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        update_values.append(user_id)

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)

        conn.commit()
        conn.close()

        logger.info(f"Updated user ID: {user_id}")

        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        }), 200

    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'error': 'Username or email already exists'
        }), 409

    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update user'
        }), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()

        logger.info(f"Deleted user ID: {user_id}")

        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete user'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Run the application
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"Starting User API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
