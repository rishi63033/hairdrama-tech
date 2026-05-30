# Auth routes
# Handles Google OAuth login and the /me endpoint
# The tricky bit was verifying the Google token on the backend instead of trusting the frontend

import os
from flask import Blueprint, request, jsonify, g
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.database import get_db_connection
from app.middleware import create_jwt, require_auth
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint("auth", __name__)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@auth_bp.route("/google", methods=["POST"])
def google_login():
    # Google login flow:
    # 1. user clicks Sign in with Google on the frontend
    # 2. frontend gets an ID token from Google and sends it here
    # 3. we verify it's legit using Google's own library
    # 4. we create or update the user in our DB
    # 5. we hand back our own JWT so the frontend can authenticate future requests
    data = request.get_json()
    if not data or "id_token" not in data:
        return jsonify({"error": "id_token is required"}), 400

    try:
        # Verify the token with Google — raises ValueError if invalid/expired
        idinfo = id_token.verify_oauth2_token(
            data["id_token"],
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as e:
        return jsonify({"error": f"Invalid Google token: {str(e)}"}), 401

    # Extract user info from the verified token payload
    google_id = idinfo["sub"]          # Unique Google user ID
    email = idinfo["email"]
    name = idinfo.get("name", email)
    avatar_url = idinfo.get("picture", "")

    # Upsert into Supabase users table
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, name, avatar_url, google_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (google_id) DO UPDATE
                    SET email = EXCLUDED.email,
                        name  = EXCLUDED.name,
                        avatar_url = EXCLUDED.avatar_url,
                        updated_at = NOW()
                RETURNING id, email, name, avatar_url, created_at
                """,
                (email, name, avatar_url, google_id),
            )
            user = dict(cur.fetchone())
            conn.commit()
    finally:
        conn.close()

    # Issue our own JWT
    token = create_jwt(str(user["id"]), user["email"])

    return jsonify({"token": token, "user": {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "avatar_url": user["avatar_url"],
    }}), 200


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    # Returns the profile of the logged-in user
    # The @require_auth decorator handles token validation before we even get here
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, name, avatar_url, created_at FROM users WHERE id = %s",
                (g.user_id,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(user)), 200
