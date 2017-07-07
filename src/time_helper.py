from datetime import datetime, timezone


def validate_time_zone(dt):
    if not dt.tzname():
        raise ValueError("Missing time zone")

def datetime_to_ms_since_epoch(dt):
    validate_time_zone(dt)
    return int(dt.timestamp() * 1000.0)

def datetime_str(dt):
    validate_time_zone(dt)
    return "{:%Y-%m-%d %H:%M:%S.%f %z}".format(dt)

def timestamp_str(timestamp_ms):
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return datetime_str(dt)
