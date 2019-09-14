import datetime
import pytz


def to_24_time(date):
    twelve_hour_time = datetime.datetime.strptime(date, '%m/%d/%Y %I:%M %p').strftime('%m/%d/%Y %H:%M')
    return datetime.datetime.strptime(twelve_hour_time, '%m/%d/%Y %H:%M')


def to_utc(timezone, date):
    return timezone.normalize(timezone.localize(date)).astimezone(pytz.utc)
