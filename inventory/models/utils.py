import datetime


def calculate_start_and_end_dates(duration: datetime.timedelta=None, end_date: datetime.date=None):
    """
    Given a duration and/or end date, return the start and end dates as appropriate.
    :param duration: how long between start and end date.  Defaults to 1 year.
    :param end_date: the end of the window.  Defaults to today.
    :return: tuple of start and end dates.
    """
    if not end_date:
        end_date = datetime.datetime.today().date()
    if duration:
        start_date = end_date - duration
    else:
        try:
            start_date = end_date.replace(year=end_date.year - 1)
        except ValueError:
            # Feb 29th might cause issues.
            start_date = end_date.replace(year=end_date.year - 1, day=end_date.day - 1)
    return start_date, end_date
