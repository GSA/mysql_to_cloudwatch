from datetime import datetime
import pytz
from ..src import time_helper


def test_datetime_to_ms_since_epoch_tzs():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)

    expected = datetime.now(pytz.utc).timestamp() * 1000
    actual = time_helper.datetime_to_ms_since_epoch(now)
    assert abs(actual - expected) < 10

def test_datetime_str():
    dt = datetime(2010, 1, 1, tzinfo=pytz.utc)
    result = time_helper.datetime_str(dt)
    assert result == "2010-01-01 00:00:00.000000 +0000"
