from datetime import datetime, timezone


def datetime_to_ms_since_epoch(dt):
    return int(dt.timestamp() * 1000.0)

def datetime_str(dt):
    return "{:%Y-%m-%d %H:%M:%S.%f %z}".format(dt)

def timestamp_str(timestamp_ms):
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return datetime_str(dt)
