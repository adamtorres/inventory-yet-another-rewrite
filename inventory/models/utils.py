import datetime
import typing

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


def pivot(
        data, row_fields: typing.Union[str | list], column_fields: typing.Union[str | list[str]], column_header,
        field_sep="|"):
    """
    Takes a list of dict and combines all the row_fields values into one list separated by column_fields.
    ```python

    For example:
    data = [
        {"date": 2025-01-01, "item": "a", "value": 11.11},
        {"date": 2025-01-01, "item": "b", "value": 22.11},
        {"date": 2025-01-02, "item": "a", "value": 33.11},
        {"date": 2025-01-03, "item": "b", "value": 44.11},
    ]
    row_fields = "date", column_fields = "item", column_header = ["a", "b"]
    ```
    Becomes:
    ```python
    {
        2025-01-01: [{"value": 11.11}, {"value": 22.11}],
        2025-02-01: [{"value": 33.11}, None],
        2025-03-01: [            None, {"value": 44.11}],
    }
    ```
    :param data: iterable of dict
    :param row_fields: list of field names to use as the row values
    :param column_fields: list of field names to use as the column values
    :param column_header: list with all the column values
    :param field_sep: separator to use if row or column fields have more than one field
    :return: dict of lists.  Each list is filled with None unless the column has a value for that given row.
    """
    output_data = {}
    if isinstance(row_fields, str):
        row_fields = [row_fields]
    if isinstance(column_fields, str):
        column_fields = [column_fields]
    exclude_fields = row_fields.copy()
    exclude_fields.extend(column_fields)
    for item in data:
        row_value = field_sep.join([str(item[k]) for k in row_fields])
        column_value = field_sep.join([str(item[k]) for k in column_fields])
        cell_value = {k: v for k, v in item.items() if k not in exclude_fields}
        if row_value not in output_data:
            output_data[row_value] = [None] * len(column_header)
        output_data[row_value][column_header.index(column_value)] = cell_value
    return output_data
