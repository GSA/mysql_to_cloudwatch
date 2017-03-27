import datetime
from .. import mysql_to_cloudwatch as mtc

def test_mysql_to_cw_log_event():
    row = [
        datetime.datetime.utcfromtimestamp(1000),
        'Query',
        'SELECT * FROM sometable'.encode()
    ]
    result = mtc.mysql_to_cw_log_event(row)
    assert result == {
        'timestamp': 1000000,
        'message': 'Query: SELECT * FROM sometable'
    }

# TODO test_get_general_log_events

# TODO test_get_general_log_events_empty
