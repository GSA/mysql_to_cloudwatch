from datetime import datetime, timezone
from ..src import time_helper


def test_datetime_str():
    dt = datetime(2010, 1, 1, tzinfo=timezone.utc)
    result = time_helper.datetime_str(dt)
    assert result == "2010-01-01 00:00:00.000000 +0000"
