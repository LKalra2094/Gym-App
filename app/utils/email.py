import resend
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Initialize Resend client
resend.api_key = os.getenv('RESEND_API_KEY')

async def send_verification_email(email: str, token: str):
    """Send verification email to user."""
    verification_link = f"http://localhost:8000/auth/verify-email?token={token}"
    
    try:
        response = resend.emails.send({
            "from": os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev'),
            "to": email,
            "subject": "Verify your email address",
            "html": f"""
            <html>
                <body>
                    <h1>Welcome to Gym Progress Tracker!</h1>
                    <p>Please verify your email address by clicking the link below:</p>
                    <p><a href="{verification_link}">Verify Email</a></p>
                    <p>If you did not create an account, please ignore this email.</p>
                </body>
            </html>
            """
        })
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

async def send_password_reset_email(email: str, token: str):
    """Send password reset email to user."""
    reset_link = f"http://localhost:8000/auth/reset-password?token={token}"
    
    try:
        response = resend.emails.send({
            "from": os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev'),
            "to": email,
            "subject": "Reset your password",
            "html": f"""
            <html>
                <body>
                    <h1>Password Reset Request</h1>
                    <p>You have requested to reset your password. Click the link below to proceed:</p>
                    <p><a href="{reset_link}">Reset Password</a></p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                    <p>This link will expire in 1 hour.</p>
                </body>
            </html>
            """
        })
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False 