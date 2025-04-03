import smtplib
import os

class ContactManager:
    def __init__(self):
        self.GMAIL_APP_PW = os.getenv("GMAIL_APP_PW")
        self.connection = smtplib.SMTP("smtp.gmail.com", 587)

    def send_email(self, from_email: "", user_email: "", message: ""):
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, self.GMAIL_APP_PW)
            server.sendmail(from_email, user_email, message)
        print("Email Sent")