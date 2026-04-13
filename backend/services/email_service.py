import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_complaint_email(to_email: str, subject: str, body: str, category: str, urgency: str) -> bool:
    host, port = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com"), int(os.getenv("EMAIL_SMTP_PORT", "587"))
    sender, pwd = os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD")
    if not sender or not pwd: return False
    
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = sender, to_email, f"[СИГНАЛ][{category}][{urgency}] Гражданска жалба"
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    try:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            s.login(sender, pwd)
            s.sendmail(sender, [to_email], msg.as_string())
        return True
    except Exception:
        return False

