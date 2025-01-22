from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import re
import uuid
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data or 'age' not in data:
        return jsonify({'error': 'Missing fields'}), 400
    if not is_valid_email(data['email']):
        return jsonify({'error': 'Invalid email'}), 400
    if not isinstance(data['age'], int) or data['age'] <= 0:
        return jsonify({'error': 'Age must be a positive integer'}), 400

    user = User(id=str(uuid.uuid4()), name=data['name'], email=data['email'], age=data['age'])
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'age': user.age}), 201

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'age': user.age}), 200

@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        if not is_valid_email(data['email']):
            return jsonify({'error': 'Invalid email'}), 400
        user.email = data['email']
    if 'age' in data:
        if not isinstance(data['age'], int) or data['age'] <= 0:
            return jsonify({'error': 'Age must be a positive integer'}), 400
        user.age = data['age']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400

    return jsonify({'id': user.id, 'name': user.name, 'email': user.email, 'age': user.age}), 200

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'name': user.name, 'email': user.email, 'age': user.age} for user in users]
    return jsonify(users_list), 200

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
