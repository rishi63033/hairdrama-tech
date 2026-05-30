# Email notification service using Gmail SMTP
# Uses Python's built-in smtplib so no extra email library needed
# You need a Gmail App Password for this - your regular password won't work
# (Google Account -> Security -> 2-Step Verification -> App Passwords)

import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587  # TLS port


def _send_email(to_email: str, subject: str, html_body: str):
    # Internal helper - opens a TLS connection and sends one email
    # will silently skip if credentials aren't configured yet
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("[Email] WARNING: Gmail credentials not configured. Email not sent.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Task Manager <{GMAIL_ADDRESS}>"
    msg["To"] = to_email

    # Attach HTML body
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())

    print(f"[Email] Sent '{subject}' to {to_email}")


def send_task_created_notification(
    assignee_email: str,
    assignee_name: str,
    task_title: str,
    task_description: str,
    creator_name: str,
    due_date: str | None,
):
    # Email sent to the assignee when someone creates a task and assigns it to them
    subject = f"📋 New Task Assigned: {task_title}"
    due_str = f"<p><strong>Due Date:</strong> {due_date}</p>" if due_date else ""
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #4F46E5;">New Task Assigned to You 🎯</h2>
        <p>Hi <strong>{assignee_name}</strong>,</p>
        <p><strong>{creator_name}</strong> has assigned you a new task:</p>
        <div style="background: #F9FAFB; padding: 16px; border-radius: 6px; margin: 16px 0;">
            <h3 style="margin: 0 0 8px 0; color: #111827;">{task_title}</h3>
            <p style="color: #6B7280; margin: 0;">{task_description or 'No description provided.'}</p>
        </div>
        {due_str}
        <p>Log in to the Task Manager to view and update your task.</p>
        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
           style="display: inline-block; background: #4F46E5; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin-top: 12px;">
           View Task
        </a>
        <p style="color: #9CA3AF; font-size: 12px; margin-top: 24px;">Task Manager — HairDrama Tech</p>
    </div>
    """
    _send_email(assignee_email, subject, html_body)


def send_task_completed_notification(
    creator_email: str,
    creator_name: str,
    task_title: str,
    assignee_name: str,
):
    # Email sent to the task creator when the assignee marks it as done
    subject = f"✅ Task Completed: {task_title}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #10B981;">Task Completed ✅</h2>
        <p>Hi <strong>{creator_name}</strong>,</p>
        <p>Great news! <strong>{assignee_name}</strong> has completed the task:</p>
        <div style="background: #F0FDF4; padding: 16px; border-radius: 6px; margin: 16px 0; border-left: 4px solid #10B981;">
            <h3 style="margin: 0; color: #111827;">{task_title}</h3>
        </div>
        <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
           style="display: inline-block; background: #10B981; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin-top: 12px;">
           View Dashboard
        </a>
        <p style="color: #9CA3AF; font-size: 12px; margin-top: 24px;">Task Manager — HairDrama Tech</p>
    </div>
    """
    _send_email(creator_email, subject, html_body)
