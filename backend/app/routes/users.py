"""
User Routes
GET /api/users  — Returns a list of all users (used for task assignment dropdown).
"""

from flask import Blueprint, jsonify, g
from app.database import get_db_connection
from app.middleware import require_auth

users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["GET"])
@require_auth
def list_users():
    """
    Returns all registered users (id, name, email, avatar_url).
    Used by the frontend to populate the 'Assign To' dropdown when creating/editing tasks.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, avatar_url FROM users ORDER BY name ASC"
            )
            users = cur.fetchall()
    finally:
        conn.close()

    return jsonify([
        {
            "id": str(u["id"]),
            "name": u["name"],
            "email": u["email"],
            "avatar_url": u["avatar_url"],
        }
        for u in users
    ]), 200
