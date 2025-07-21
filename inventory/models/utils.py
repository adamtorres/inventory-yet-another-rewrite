import datetime

import dateparser
from django.apps import apps


def calculate_start_and_end_dates(duration: datetime.timedelta=None, end_date: datetime.date=None):
    """
    Given a duration and/or end date, return the start and end dates as appropriate.
    :param duration: how long between start and end date.  Defaults to 1 year.
    :param end_date: the end of the window.  Defaults to today.
    :return: tuple of start and end dates.
    """
    # Getting the model this way to avoid circular dependency
    Setting = apps.get_model('inventory', 'Setting')
    duration_andor_end_date = Setting.objects.get_report_date_range()
    x = {
        "duration": (
                duration or duration_andor_end_date.get("duration") or
                (datetime.datetime.today().date() - dateparser.parse("1 year").date())),
        "end_date": end_date or duration_andor_end_date.get("end_date") or datetime.datetime.today().date()
    }
    if x["duration"]:
        start_date = x["end_date"] - x["duration"]
    else:
        try:
            start_date = x["end_date"].replace(year=x["end_date"].year - 1)
        except ValueError:
            # Feb 29th might cause issues.
            start_date = x["end_date"].replace(year=x["end_date"].year - 1, day=x["end_date"].day - 1)
    return start_date, x["end_date"]
