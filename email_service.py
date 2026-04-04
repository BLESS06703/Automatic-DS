# email_service.py - Send diagnostic reports via email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    def __init__(self):
        # For testing, use Gmail's SMTP (free)
        # You'll need to enable "Less secure app access" or use App Password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "your-email@gmail.com"  # Change this
        self.sender_password = "your-app-password"  # Change this
    
    def send_report(self, recipient_email, report_file, customer_name, vehicle_info):
        """Send diagnostic report via email"""
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Diagnostic Report for {vehicle_info['make']} {vehicle_info['model']}"
            
            # Email body
            body = f"""
            Dear {customer_name},
            
            Please find attached the diagnostic report for your {vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']}.
            
            Severity: {vehicle_info.get('severity', 'Medium')}
            
            Summary:
            {vehicle_info.get('results', 'Diagnostic completed')}
            
            For questions or to schedule service, please contact us.
            
            Best regards,
            Bless Digital Auto Care
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report
            with open(report_file, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(report_file)}')
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Email sent successfully"
        except Exception as e:
            return False, str(e)
