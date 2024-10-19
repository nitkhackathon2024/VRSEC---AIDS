from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)  # This will allow all domains to access your Flask API

# Configure logging
logging.basicConfig(level=logging.WARNING)

# Define the base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Set the database URI to point to users.db in the backend directory
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contact_no = db.Column(db.String(15), nullable=False)
    skills = db.Column(db.Text)  # Add a column for skills
    areas_for_improvement = db.Column(db.Text)  # Add a column for areas of improvement

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/<path:path>')
def send_html(path):
    return send_from_directory('', path)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    contact = data.get('contact')

    if username and email and contact:
        user = User(username=username, email=email, contact_no=contact)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    return jsonify({"error": "Invalid input"}), 400

@app.route('/submit-skills', methods=['POST'])
def submit_skills():
    data = request.json
    username = data.get('username')
    skills = data.get('skills')
    areas = data.get('areas')

    if not username or not skills or not areas:
        return jsonify({"error": "Missing fields"}), 400

    # Update existing user or create a new one
    user = User.query.filter_by(username=username).first()
    if user:
        user.skills = skills
        user.areas_for_improvement = areas
        db.session.commit()
        return jsonify({"message": "Skills and areas updated successfully!"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/submit-user-details', methods=['POST'])
def submit_user_details():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    contact = data.get('contact')

    if username and email and contact:
        user = User.query.filter_by(username=username).first()
        if user:
            user.email = email
            user.contact_no = contact
            db.session.commit()
            return jsonify({"message": "User details updated successfully!"}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"error": "Missing fields"}), 400

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = []
    for user in users:
        users_list.append({
            'username': user.username,
            'email': user.email,
            'contact_no': user.contact_no,
            'skills': user.skills,
            'areas_for_improvement': user.areas_for_improvement
        })
    return jsonify(users_list), 200

@app.route('/match_peers', methods=['POST'])
def match_peers():
    input_areas = request.json.get('areas', '').split(',')
    input_areas = [area.strip().lower() for area in input_areas]

    matched_peers = User.query.all()
    results = []

    for peer in matched_peers:
        if peer.areas_for_improvement is None:
            logging.warning(f"User {peer.username} has no areas for improvement.")
            continue  # Skip users without areas for improvement

        areas = [area.strip().lower() for area in peer.areas_for_improvement.split(',')]
        if any(area in areas for area in input_areas):
            results.append(peer.username)

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates database tables if they don't exist
    app.run(host='127.0.0.1', port=5001)
