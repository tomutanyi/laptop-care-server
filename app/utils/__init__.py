from flask_mail import Message
from flask import current_app
from app import mail

def send_email(subject, recipients, body):
    """
    Helper function to send email notifications.
    """
    msg = Message(subject, recipients=recipients, body=body, sender=current_app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)
