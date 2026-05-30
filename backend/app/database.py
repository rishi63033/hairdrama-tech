"""
Database connection module.
Uses psycopg2 to connect to Supabase PostgreSQL.
A new connection is created per request (simple pooling approach suitable for small apps).
"""

import psycopg2
import psycopg2.extras  # Enables dict-style row access
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """
    Opens a new PostgreSQL connection to Supabase.
    Returns a connection with RealDictCursor so rows come back as dicts.
    Always close the connection in a finally block or use it as a context manager.
    """
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=psycopg2.extras.RealDictCursor,  # rows → dict
    )
    return conn
