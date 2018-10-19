import os
import re

broker_url = os.environ['CELERY_BROKER']
task_ignore_result = True

# task queue definition
task_message_queue = os.environ['CELERY_MESSAGE_QUEUE']
task_event_queue = os.environ['CELERY_EVENT_QUEUE']
task_review_queue = os.environ['CELERY_REVIEW_QUEUE']

# routes for app to send task to
task_routes = {
    'data.email.task_send_email': task_message_queue,
    'monitors.tasks.url_request': task_message_queue,
    'user_feedback': task_event_queue,
    'event_service': task_event_queue,
    'text_review': task_review_queue,
    'push_notify_to_user': task_review_queue
}

