from celery import Celery, Task
from . import celeryconfig
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data.settings')


class MyTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        subject = str(exc)
        body = str(einfo) + "\ntask_id=%s\nargs=%s\nkwargs=%s" % (task_id, args, kwargs)
        app.send_task('data.email.task_send_email', (subject, body,))


app = Celery('data', task_cls=MyTask)
app.config_from_object(celeryconfig)


def send_task(name, *args, **kwargs):
    app.send_task(name, args, kwargs)
