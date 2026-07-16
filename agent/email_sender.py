import smtplib
from email.message import EmailMessage
from agent.logger import setup_logger

logger = setup_logger("EmailSender")

class EmailSender:
    def __init__(self, email_address: str, email_password: str):
        self.email_address = email_address
        self.email_password = email_password
        # using gmail standard SMTP as a baseline
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, to_email: str, subject: str, content: str):
        """Sends an email via SMTP."""
        logger.info(f"Sending Email to {to_email}")
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = f"AI Attendance system <{self.email_address}>"
        msg['To'] = to_email
        
        # Adding a plain text alternative helps tremendously with spam filters
        plain_text = "You have been marked ABSENT. Please view this email in an HTML-compatible client to see the full alert details."
        msg.set_content(plain_text)
        
        # Add the generated HTML as the primary alternative
        msg.add_alternative(content, subtype='html')

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            logger.info(f"Email Sent to {to_email}")
        except Exception as e:
            logger.error(f"SMTP failure when sending to {to_email}: {e}")
            raise
