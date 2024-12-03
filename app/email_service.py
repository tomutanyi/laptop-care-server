import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import current_app
from threading import Thread
from queue import Queue, Empty
import traceback
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.email_queue = Queue()
        self.email_thread = None
        self._stop_thread = False

    def _get_smtp_connection(self):
        """
        Get SMTP connection with fallback to environment variables
        and explicit configuration.
        """
        from flask import current_app
        import os

        try:
            # Try to get configuration from current_app
            mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = current_app.config.get('MAIL_PORT', 587)
            mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
        except RuntimeError:
            # Fallback to environment variables if no app context
            mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            mail_port = int(os.environ.get('MAIL_PORT', 587))
            mail_use_tls = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
            mail_username = os.environ.get('MAIL_USERNAME')
            mail_password = os.environ.get('MAIL_PASSWORD')

        # Validate required configuration
        if not mail_username or not mail_password:
            logger.error("Email configuration is incomplete. Cannot send emails.")
            return None

        try:
            # Create SMTP connection
            if mail_use_tls:
                smtp_conn = smtplib.SMTP(mail_server, mail_port)
                smtp_conn.starttls()
            else:
                smtp_conn = smtplib.SMTP(mail_server, mail_port)
            
            # Login to the SMTP server
            smtp_conn.login(mail_username, mail_password)
            
            return smtp_conn
        except Exception as e:
            logger.error(f"SMTP Connection Error: {str(e)}")
            return None

    def _email_worker(self):
        """Background worker to process email queue."""
        while not self._stop_thread:
            try:
                # Wait for email with a timeout
                try:
                    email_task = self.email_queue.get(timeout=1)
                except Empty:
                    continue

                # Get SMTP connection
                smtp_connection = self._get_smtp_connection()
                if not smtp_connection:
                    logger.error("Could not establish SMTP connection")
                    self.email_queue.task_done()  # Mark task as done if we couldn't process it
                    continue

                try:
                    # Send the email
                    smtp_connection.send_message(email_task['message'])
                    logger.info(f"Email sent to {email_task['recipient']}")
                except Exception as send_error:
                    logger.error(f"Failed to send email: {send_error}")
                finally:
                    # Close the SMTP connection
                    smtp_connection.quit()
                    self.email_queue.task_done()  # Mark task as done after processing

            except Exception as e:
                logger.error(f"Error in email worker: {e}")
                logger.error(traceback.format_exc())

    def start_email_service(self):
        """Start the email service background thread."""
        if self.email_thread and self.email_thread.is_alive():
            return

        self._stop_thread = False
        self.email_thread = Thread(target=self._email_worker, daemon=True)
        self.email_thread.start()
        logger.info("Email service started")

    def stop_email_service(self):
        """Gracefully stop the email service."""
        self._stop_thread = True
        if self.email_thread:
            self.email_thread.join()
        logger.info("Email service stopped")

    def send_email(self, subject, recipient, html_body, attachments=None):
        """
        Queue an email for sending with optional attachments.
        
        Args:
            subject (str): Email subject
            recipient (str): Recipient email address
            html_body (str): HTML content of the email
            attachments (list, optional): List of dictionaries with file details
                Each attachment dict should have:
                - 'filename': name of the file
                - 'content': file content as bytes
                - 'mimetype': MIME type of the file (e.g., 'application/pdf')
        
        Returns:
            bool: True if email was queued successfully, False otherwise
        """
        try:
            # Create multipart message
            message = MIMEMultipart()
            message['From'] = current_app.config.get('MAIL_DEFAULT_SENDER')
            message['To'] = recipient
            message['Subject'] = subject
            
            # Attach HTML body
            message.attach(MIMEText(html_body, 'html'))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(attachment['content'], _subtype=attachment.get('subtype', 'octet-stream'))
                    part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
                    message.attach(part)
            
            # Prepare email task
            email_task = {
                'message': message,
                'recipient': recipient
            }
            
            # Queue the email
            self.email_queue.put(email_task)
            
            logger.info(f"Email to {recipient} queued successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to queue email: {e}")
            logger.error(traceback.format_exc())
            return False

    def send_jobcard_notification(self, client_name, client_email, jobcard_id, 
                                   problem_description, device_model, device_brand):
        """
        Send a jobcard notification email.
        
        Args:
            client_name (str): Name of the client
            client_email (str): Email of the client
            jobcard_id (int): ID of the jobcard
            problem_description (str): Description of the problem
            device_model (str): Model of the device
            device_brand (str): Brand of the device
        
        Returns:
            bool: True if email was queued successfully, False otherwise
        """
        try:
            logger.info(f"Preparing to send jobcard notification email")
            logger.info(f"Client Details - Name: {client_name}, Email: {client_email}")
            logger.info(f"Jobcard Details - ID: {jobcard_id}, Problem: {problem_description}")
            logger.info(f"Device Details - Model: {device_model}, Brand: {device_brand}")

            subject = f'New Job Card #{jobcard_id} Created - Laptop Care'
            
            html_body = f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
                    <h2 style="color: #2c3e50;">New Job Card Created</h2>
                    <p>Dear {client_name},</p>
                    
                    <p>A new job card has been created for your device with the following details:</p>
                    
                    <div style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: white;">
                        <p><strong>Job Card Number:</strong> #{jobcard_id}</p>
                        <p><strong>Device:</strong> {device_brand} {device_model}</p>
                        <p><strong>Problem Description:</strong> {problem_description}</p>
                    </div>
                    
                    <p>Our technicians will assess your device and begin work on it shortly. You will receive updates 
                    as we progress with the repairs.</p>
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    
                    <p style="margin-top: 20px; font-style: italic;">Best regards,<br>
                    Laptop Care Team</p>
                </div>
            </body>
            </html>
            '''
            
            result = self.send_email(subject, client_email, html_body)
            logger.info(f"Email sending result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to prepare jobcard notification email: {e}")
            logger.error(traceback.format_exc())
            return False

# Create a global email service instance
email_service = EmailService()
