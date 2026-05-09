from config import users_collection
import bcrypt

def create_user(name, email, password):
    existing = users_collection.find_one({"email": email})
    if existing:
        return None, "Email already exists"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user = {
        "name": name,
        "email": email,
        "password": hashed,
        "created_at": __import__('datetime').datetime.utcnow()
    }
    
    result = users_collection.insert_one(user)
    return str(result.inserted_id), None

def find_user_by_email(email):
    return users_collection.find_one({"email": email})

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)