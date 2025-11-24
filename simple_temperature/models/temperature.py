import decimal
from django.db import connection, models


def get_location_names_from_temperature_qs(qs):
    all_locations = set()
    for reading in qs:
        all_locations.update(reading.location_readings.keys())
    return sorted(list(all_locations))


class TemperatureManager(models.Manager):
    def flatten_qs(self, qs):
        """
        qs = Temperature.objects.filter(datetime range)
        Temperature.location_readings = {"location name": "0.00", "location name": "0.00"}
        Want:
        [ { "name": "event_datetime", "data": [list of the datetimes in qs"] },
          { "name": "name of the series", "data": [list of the temperatures"] },
          { "name": "name of the series", "data": [list of the temperatures"] }, ]
        """
        all_locations = get_location_names_from_temperature_qs(qs)
        graph_data_tmp = {"event_datetime": []}
        graph_data_tmp.update({k: [] for k in all_locations})
        for minute in qs:
            graph_data_tmp["event_datetime"].append(minute.event_datetime)
            for location_name in all_locations:
                temperature_value = None
                if location_name in minute.location_readings:
                    temperature_value = decimal.Decimal(minute.location_readings[location_name])
                graph_data_tmp[location_name].append(temperature_value)
        non_datetime_data = [
            {"name": k, "data": graph_data_tmp[k]} for k in graph_data_tmp.keys()]
        return non_datetime_data

    def get_last_event_datetime(self):
        return self.aggregate(
            left_off_at=models.Max("event_datetime"),
            count=models.Count("id"),
        )


class Temperature(models.Model):
    event_datetime = models.DateTimeField()
    location_readings = models.JSONField(default=dict)

    objects = TemperatureManager()

    def __str__(self):
        location_names = sorted(self.location_readings.keys())
        readings = []
        for ln in location_names:
            try:
                val = f"{round(decimal.Decimal(self.location_readings[ln]), 0)}F"
            except decimal.InvalidOperation:
                val = "n/a"
            readings.append(f"{ln}: {val}")
        return f"{self.event_datetime}| {", ".join(readings)}"

    @classmethod
    def get_all_locations(cls):
        all_locations_sql = """
                            SELECT DISTINCT json_unquote(json_key) as location_name
                              FROM """ + cls._meta.db_table + """,
                                   json_table(
                                           json_keys(location_readings),
                                           '$[*]' COLUMNS (json_key JSON PATH '$')
                                   ) t; \
                            """
        with connection.cursor() as cursor:
            cursor.execute(all_locations_sql)
            return [r[0] for r in cursor.fetchall()]
