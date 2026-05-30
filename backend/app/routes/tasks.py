# Task routes - this is the main bulk of the backend
# Handles create/read/update/delete plus the mark-complete endpoint
# Email notifications are sent async so we don't slow down the API response

from flask import Blueprint, request, jsonify, g
from app.database import get_db_connection
from app.middleware import require_auth
from app.email_service import (
    send_task_created_notification,
    send_task_completed_notification,
)
import threading

tasks_bp = Blueprint("tasks", __name__)


def _send_email_async(fn, *args, **kwargs):
    """Run email sending in a background thread so API response is not delayed."""
    thread = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    thread.start()


@tasks_bp.route("", methods=["GET"])
@require_auth
def list_tasks():
    # fetch tasks where the user is either the one who created it or the one it's assigned to
    # sorted by newest first
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.id, t.title, t.description, t.status, t.priority,
                    t.due_date, t.created_at, t.updated_at, t.completed_at,
                    creator.id   AS creator_id,
                    creator.name AS creator_name,
                    creator.email AS creator_email,
                    creator.avatar_url AS creator_avatar,
                    assignee.id   AS assignee_id,
                    assignee.name AS assignee_name,
                    assignee.email AS assignee_email,
                    assignee.avatar_url AS assignee_avatar
                FROM tasks t
                JOIN users creator  ON t.creator_id  = creator.id
                LEFT JOIN users assignee ON t.assignee_id = assignee.id
                WHERE t.creator_id = %s OR t.assignee_id = %s
                ORDER BY t.created_at DESC
                """,
                (g.user_id, g.user_id),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify([_format_task(dict(r)) for r in rows]), 200


@tasks_bp.route("", methods=["POST"])
@require_auth
def create_task():
    # Create a new task
    # assignee_id is optional - if not provided it just stays unassigned
    # email is sent in the background so the user doesn't have to wait for it
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    title = data["title"].strip()
    description = data.get("description", "").strip()
    priority = data.get("priority", "medium")
    due_date = data.get("due_date")  # ISO date string or None
    assignee_id = data.get("assignee_id")  # UUID string or None

    if priority not in ("low", "medium", "high"):
        return jsonify({"error": "priority must be low, medium, or high"}), 400

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Insert the task
            cur.execute(
                """
                INSERT INTO tasks (title, description, priority, due_date, creator_id, assignee_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (title, description, priority, due_date, g.user_id, assignee_id),
            )
            task_id = cur.fetchone()["id"]
            conn.commit()

            # Fetch the full task with joins for the response
            cur.execute(
                """
                SELECT
                    t.id, t.title, t.description, t.status, t.priority,
                    t.due_date, t.created_at, t.updated_at, t.completed_at,
                    creator.id AS creator_id, creator.name AS creator_name,
                    creator.email AS creator_email, creator.avatar_url AS creator_avatar,
                    assignee.id AS assignee_id, assignee.name AS assignee_name,
                    assignee.email AS assignee_email, assignee.avatar_url AS assignee_avatar
                FROM tasks t
                JOIN users creator ON t.creator_id = creator.id
                LEFT JOIN users assignee ON t.assignee_id = assignee.id
                WHERE t.id = %s
                """,
                (task_id,),
            )
            task = dict(cur.fetchone())
    finally:
        conn.close()

    # Send email notification to assignee (if different from creator)
    if (
        task.get("assignee_email")
        and task["assignee_id"] != task["creator_id"]
    ):
        _send_email_async(
            send_task_created_notification,
            assignee_email=task["assignee_email"],
            assignee_name=task["assignee_name"],
            task_title=task["title"],
            task_description=task["description"],
            creator_name=task["creator_name"],
            due_date=str(task["due_date"]) if task["due_date"] else None,
        )

    return jsonify(_format_task(task)), 201


@tasks_bp.route("/<task_id>", methods=["GET"])
@require_auth
def get_task(task_id):
    """Fetch a single task. User must be creator or assignee."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    t.id, t.title, t.description, t.status, t.priority,
                    t.due_date, t.created_at, t.updated_at, t.completed_at,
                    creator.id AS creator_id, creator.name AS creator_name,
                    creator.email AS creator_email, creator.avatar_url AS creator_avatar,
                    assignee.id AS assignee_id, assignee.name AS assignee_name,
                    assignee.email AS assignee_email, assignee.avatar_url AS assignee_avatar
                FROM tasks t
                JOIN users creator ON t.creator_id = creator.id
                LEFT JOIN users assignee ON t.assignee_id = assignee.id
                WHERE t.id = %s AND (t.creator_id = %s OR t.assignee_id = %s)
                """,
                (task_id, g.user_id, g.user_id),
            )
            task = cur.fetchone()
    finally:
        conn.close()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(_format_task(dict(task))), 200


@tasks_bp.route("/<task_id>", methods=["PUT"])
@require_auth
def update_task(task_id):
    """Update task fields. Only the creator can update."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    allowed_fields = {"title", "description", "priority", "due_date", "assignee_id", "status"}
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    # Build dynamic SET clause safely using parameterized queries
    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [task_id, g.user_id]

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE tasks SET {set_clause} WHERE id = %s AND creator_id = %s RETURNING id",
                values,
            )
            updated = cur.fetchone()
            if not updated:
                return jsonify({"error": "Task not found or you are not the creator"}), 404
            conn.commit()

            # Return full updated task
            cur.execute(
                """
                SELECT t.id, t.title, t.description, t.status, t.priority,
                    t.due_date, t.created_at, t.updated_at, t.completed_at,
                    creator.id AS creator_id, creator.name AS creator_name,
                    creator.email AS creator_email, creator.avatar_url AS creator_avatar,
                    assignee.id AS assignee_id, assignee.name AS assignee_name,
                    assignee.email AS assignee_email, assignee.avatar_url AS assignee_avatar
                FROM tasks t
                JOIN users creator ON t.creator_id = creator.id
                LEFT JOIN users assignee ON t.assignee_id = assignee.id
                WHERE t.id = %s
                """,
                (task_id,),
            )
            task = dict(cur.fetchone())
    finally:
        conn.close()

    return jsonify(_format_task(task)), 200


@tasks_bp.route("/<task_id>/complete", methods=["PATCH"])
@require_auth
def complete_task(task_id):
    # Either the creator or the assignee can mark a task complete
    # sends an email to the creator to let them know
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET status = 'completed', completed_at = NOW()
                WHERE id = %s AND (creator_id = %s OR assignee_id = %s)
                RETURNING id
                """,
                (task_id, g.user_id, g.user_id),
            )
            updated = cur.fetchone()
            if not updated:
                return jsonify({"error": "Task not found or permission denied"}), 404
            conn.commit()

            # Fetch full task for email data
            cur.execute(
                """
                SELECT t.title,
                    creator.email AS creator_email, creator.name AS creator_name,
                    assignee.name AS assignee_name
                FROM tasks t
                JOIN users creator ON t.creator_id = creator.id
                LEFT JOIN users assignee ON t.assignee_id = assignee.id
                WHERE t.id = %s
                """,
                (task_id,),
            )
            task_info = dict(cur.fetchone())
    finally:
        conn.close()

    # Email the creator about completion
    _send_email_async(
        send_task_completed_notification,
        creator_email=task_info["creator_email"],
        creator_name=task_info["creator_name"],
        task_title=task_info["title"],
        assignee_name=task_info.get("assignee_name") or "Someone",
    )

    return jsonify({"message": "Task marked as completed"}), 200


@tasks_bp.route("/<task_id>", methods=["DELETE"])
@require_auth
def delete_task(task_id):
    """Delete a task. Only the creator can delete."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s AND creator_id = %s RETURNING id",
                (task_id, g.user_id),
            )
            deleted = cur.fetchone()
            if not deleted:
                return jsonify({"error": "Task not found or permission denied"}), 404
            conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "Task deleted"}), 200


def _format_task(row: dict) -> dict:
    """Restructures a flat DB row into a nested task object for the API response."""
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "priority": row["priority"],
        "due_date": str(row["due_date"]) if row["due_date"] else None,
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
        "completed_at": str(row["completed_at"]) if row.get("completed_at") else None,
        "creator": {
            "id": str(row["creator_id"]),
            "name": row["creator_name"],
            "email": row["creator_email"],
            "avatar_url": row["creator_avatar"],
        },
        "assignee": {
            "id": str(row["assignee_id"]),
            "name": row["assignee_name"],
            "email": row["assignee_email"],
            "avatar_url": row["assignee_avatar"],
        } if row.get("assignee_id") else None,
    }
