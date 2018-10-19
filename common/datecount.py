from datetime import datetime, timedelta
from django.utils import timezone

first_day = timezone.make_aware(datetime(2017, 10, 14, 0, 0, 0))


class DateTimeCount(object):

    def __init__(self, default_date=None):
        self.now = timezone.make_aware(default_date) if default_date else timezone.localtime()
        self.delta = self.now - first_day

    @property
    def days(self):
        return self.delta.days

    @property
    def seconds(self):
        return self.delta.days*86400+self.delta.seconds


def seconds_to_datetime(seconds):
    try:
        s = int(seconds)
        return first_day + timedelta(seconds=s)
    except Exception:
        return None


def str_to_datetime(dt_str):
    """
    2018/02/15 00:00:00
    :param dt_str: 
    :return: 
    """
    year = int(dt_str[:4])
    month = int(dt_str[5:7])
    day = int(dt_str[8:10])
    hour = int(dt_str[11:13])
    minute = int(dt_str[14:16])
    second = int(dt_str[17:19])
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
