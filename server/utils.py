import hashlib
import os
import smtplib
import sqlite3
from email.message import EmailMessage

# Set your credentials here to send email
from threading import Lock

credentials = os.environ.get("EMAIL_ADDRESS"), os.environ.get("EMAIL_PASSWORD")


def send_email(email: EmailMessage) -> None:
    if credentials[0] is None or credentials[1] is None:
        print(f"No email credentials are set, printing email:\n{email}")
        return

    try:
        with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(*credentials)
            smtp_server.send_message(email)
    except Exception as e:
        print(f"Failed to send email, printing email:\n{email}\n\nERROR:")
        raise e


class QueryExecutor:
    def __init__(self, path):
        self.db = sqlite3.connect(path)

    def __call__(self, query: str, parameters: list) -> list:
        result = list(self.db.execute(query, parameters))
        self.db.commit()
        return result


def encrypt(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def mutex(function):
    def inner(*args, **kwargs):
        lock = Lock()
        lock.acquire()
        result = function(*args, **kwargs)
        lock.release()
        return result

    return inner
