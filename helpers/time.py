from datetime import datetime
import pytz


def to_24_time(date):
    twelve_hour_time = datetime.strptime(date, '%m/%d/%Y %I:%M %p').strftime('%m/%d/%Y %H:%M')
    return datetime.strptime(twelve_hour_time, '%m/%d/%Y %H:%M')


def to_timezone(timezone, date, target_timezone):
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)

    if isinstance(target_timezone, str):
        target_timezone = pytz.timezone(target_timezone)

    if isinstance(date, str):
        date = datetime.fromtimestamp(float(date))

    return timezone.localize(date).astimezone(target_timezone)


def to_utc(timezone, date):
    return to_timezone(timezone, date, pytz.utc)
