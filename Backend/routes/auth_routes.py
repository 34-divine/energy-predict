from flask import Blueprint, request, jsonify
from models.user_model import create_user, find_user_by_email, verify_password
from auth import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    user_id, error = create_user(name, email, password)
    if error:
        return jsonify({"error": error}), 400

    token = generate_token(user_id, email)
    return jsonify({"message": "Registration successful", "token": token}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    user = find_user_by_email(email)
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not verify_password(password, user['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(str(user['_id']), email)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "name": user['name'],
        "email": user['email']
    }), 200

@auth_bp.route('/me', methods=['GET'])
def me():
    from auth import token_required
    token = None
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].split(" ")[1]
    if not token:
        return jsonify({"error": "Token is missing"}), 401
    import jwt
    from config import JWT_SECRET
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return jsonify({"user_id": data["user_id"], "email": data["email"]}), 200
    except:
        return jsonify({"error": "Invalid token"}), 401