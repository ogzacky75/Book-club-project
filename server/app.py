# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory fake user store for demo purposes
users = {}

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if username in users:
        return jsonify({'error': 'User already exists'}), 400

    # Save user (in-memory for now)
    users[username] = {
        'email': email,
        'password': password
    }

    return jsonify({
        'message': 'Signup successful',
        'access_token': 'mocked_token_123',
        'user': {
            'username': username,
            'email': email
        }
    }), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = users.get(username)

    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Login successful',
        'access_token': 'mocked_token_123',
        'user': {
            'username': username,
            'email': user['email']
        }
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
