import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


def send_email_to_samantha(patient_data: dict) -> bool:
    """
    Send a formatted appointment-request email to the clinic manager.
    Returns True on success, False on failure.
    """
    subject = f"New Appointment Request: {patient_data.get('name', 'Unknown')}"

    body = f"""
Hi Samantha,

A new appointment request has come in through SmileBot! Here are the details:

  Patient Name : {patient_data.get("name", "N/A")}
  Phone Number : {patient_data.get("phone", "N/A")}
  Email        : {patient_data.get("email", "N/A")}
  Preferred    : {patient_data.get("preferred_time", "N/A")}
  Reason       : {patient_data.get("reason", "General appointment")}

Please reach out to the patient to confirm the exact appointment time.

— SmileBot (A Beautiful Smile Virtual Receptionist)
""".strip()

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = settings.CLINIC_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_APP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, settings.CLINIC_EMAIL, msg.as_string())
        logger.info("Email sent successfully for patient: %s", patient_data.get("name"))
        return True
    except Exception:
        logger.exception("Failed to send email for patient: %s", patient_data.get("name"))
        return False
