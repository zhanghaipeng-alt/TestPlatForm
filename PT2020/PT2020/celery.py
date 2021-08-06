from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PT2020.settings')

app = Celery('PT2020')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    time.sleep(10)
    print("haha")

def debug_task1():
    time.sleep(10)
    print("haha")