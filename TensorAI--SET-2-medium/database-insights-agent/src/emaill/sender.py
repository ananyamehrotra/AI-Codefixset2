import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import os

def send_email(subject, body, recipient, attachments=None):
    """Send email with report and attachments."""
    print(f"📧 Preparing to send email to {recipient}")
    
    # Set up the SMTP server
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not all([smtp_server, sender_email, sender_password]):
        print("❌ Email credentials not found in environment variables")
        print("📁 Report saved locally - check output/reports/ folder")
        return False

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject

        # Attach the email body as plain text
        msg.attach(MIMEText(body, 'plain'))

        # Attach any files
        if attachments:
            for attachment in attachments:
                if os.path.exists(attachment):
                    attach_file(msg, attachment)
                else:
                    print(f"⚠️ Attachment not found: {attachment}")

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient], msg.as_string())
        
        print(f"✅ Email sent successfully to {recipient}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print("📁 Report saved locally - check output/reports/ folder")
        return False

def attach_file(msg, file_path):
    """Attach a file to the email message."""
    ctype, encoding = mimetypes.guess_type(file_path)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    
    maintype, subtype = ctype.split("/", 1)
    
    with open(file_path, "rb") as fp:
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(file_path)}"'
        )
        msg.attach(attachment)
    
    print(f"  📎 Attached: {os.path.basename(file_path)}")