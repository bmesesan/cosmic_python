import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["Subject"] = "WSL SMTP Test"
msg["From"] = "test@example.com"
msg["To"] = "recipient@example.com"
msg.set_content("Hello from WSL!")

with smtplib.SMTP("localhost", 1025) as smtp:
    smtp.send_message(msg)

print("Sent")