from datetime import datetime, timedelta
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


def days_ago(days, date=datetime.today().strftime('%m/%d/%Y')):
    date = datetime.strptime(date, '%m/%d/%Y')
    destination_date = date - timedelta(days=days)
    return destination_date.strftime('%m/%d/%Y')


def last_update_date(date: str = datetime.today().strftime('%m/%d/%Y')):
    date = datetime.strptime(date, '%m/%d/%Y')
    weekday = date.weekday()
    days_to_friday = weekday - 4

    if days_to_friday < 0:
        days_to_friday *= -1

    if weekday > 4:
        return (date - timedelta(days=days_to_friday)).strftime('%m-%d-%Y')
    elif weekday < 4:
        return ((date + timedelta(days=days_to_friday)) - timedelta(weeks=1)).strftime('%m-%d-%Y')
    else:
        return date.strftime('%m-%d-%Y')
