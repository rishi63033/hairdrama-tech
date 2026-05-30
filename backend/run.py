"""
Backend entry point.
Run with:  python run.py           (development)
           gunicorn run:app        (production)
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Debug mode ON for local development only.
    # In production, gunicorn handles this.
    app.run(debug=True, port=5000)
