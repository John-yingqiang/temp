from django.core.mail.backends.base import BaseEmailBackend
from .celery import app


def send_email(subject, body):
    app.send_task('data.email.task_send_email', (subject, body,))


class EmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        for message in email_messages:
            send_email(message.subject, message.body)
