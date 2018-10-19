from general.celery import send_task
from time import time


class UserEvent(object):

    def __init__(self, request):
        token = request.token_data
        self.branch = token.get('branch', 'unknown')
        self.version = token.get('version', 'unknown')
        self.device_channel = token.get('channel', 'unknown')  # channel of device
        self.did = token.get('did')
        self.pid = token.get('pid')
        self.os = request.get_os()
        self.ip = request.ip_address
        self.cid = token.get('cid')  # channel of user
        self.uid = token.get('number')
        self.ts = int(time())

    def _send_task(self, name, **kwargs):
        send_task('user_feedback', action=name, ts=self.ts, pid=self.pid, branch=self.branch, os=self.os,
                  version=self.version, cid=self.cid, uid=self.uid, ip=self.ip,
                  did=self.did, device_channel=self.device_channel, **kwargs)

    def user_feedback(self, sort, content):
        self._send_task('user_feedback', sort=sort, content=content)


class ServiceEvent(object):

    def __init__(self, number):
        self.number = number
        self.ts = int(time())

    def ret_heiniu(self, result):
        send_task('event_service', 'service_heiniui', number=self.number, result=result, ts=self.ts)
