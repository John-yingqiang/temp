from general.settings import TIME_ZONE
import pytz


def convert_to_local_time(utc_time):
    time_save = utc_time.replace(tzinfo=pytz.utc)
    show_time = time_save.astimezone(pytz.timezone(TIME_ZONE))
    return show_time.strftime('%Y/%m/%d %H:%M:%S')
