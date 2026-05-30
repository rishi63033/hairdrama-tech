# JWT auth middleware
# The require_auth decorator is used on any route that needs a logged-in user
# It reads the Bearer token from the Authorization header and decodes it

import os
import jwt
from functools import wraps
from flask import request, jsonify, g
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret")
JWT_ALGORITHM = "HS256"


def create_jwt(user_id: str, email: str) -> str:
    # Creates a signed JWT for the given user
    # not adding expiry for now to keep things simple, can add later if needed
    payload = {"sub": user_id, "email": email}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def require_auth(f):
    # Decorator that checks the JWT in the Authorization header
    # Puts user_id and user_email into Flask's g context so routes can access them
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            g.user_id = payload["sub"]
            g.user_email = payload["email"]
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated
