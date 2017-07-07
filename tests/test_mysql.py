from datetime import datetime, timezone
import pymysql
import pytest
from ..src import mysql


# the number of events that will show up after clear_logs()
BASELINE_NUM_EVENTS = 1


@pytest.fixture
def conn():
    conn = pymysql.connect(host='mysql', db='mysql')
    yield conn
    conn.close()

@pytest.fixture
def db(conn):
    db = mysql.MySQL(conn)
    db.enable_logs()
    db.clear_logs()
    return db

def test_mysql_to_cw_log_event_string():
    row = [
        datetime.utcfromtimestamp(1000),
        'Query',
        'SELECT * FROM sometable'
    ]
    result = mysql.mysql_to_cw_log_event(row)
    assert result == {
        'timestamp': 1000000,
        'message': 'Query: SELECT * FROM sometable'
    }

def test_mysql_to_cw_log_event_bytes():
    row = [
        datetime.fromtimestamp(1000, timezone.utc),
        'Query',
        'SELECT * FROM sometable'.encode()
    ]
    result = mysql.mysql_to_cw_log_event(row)
    assert result == {
        'timestamp': 1000000,
        'message': 'Query: SELECT * FROM sometable'
    }

def test_mysql_to_cw_log_event_no_tz():
    row = [
        datetime.fromtimestamp(1000),
        'Query',
        'SELECT * FROM sometable'.encode()
    ]
    result = mysql.mysql_to_cw_log_event(row)
    assert result == {
        'timestamp': 1000000,
        'message': 'Query: SELECT * FROM sometable'
    }

def test_enable_logs_skip_if_enabled(db):
    start = datetime.now(tz=timezone.utc)

    db.enable_logs()

    events = db.get_general_log_events(start)
    print(events)
    for event in events:
        assert 'SET ' not in event['message']

def test_enable_logs_permission_denied(db):
    with db.transact() as cursor:
        cursor.execute("SET GLOBAL general_log = 'OFF'")
        cursor.execute("CREATE USER IF NOT EXISTS 'nonsuper'@'%'")
        cursor.execute("GRANT SELECT ON *.* TO 'nonsuper'@'%'")

    conn2 = pymysql.connect(host='mysql', db='mysql', user='nonsuper')
    try:
        db2 = mysql.MySQL(conn2)
        db2.enable_logs()
        # shouldn't raise exception
    finally:
        conn2.close()

def test_clear_logs(db):
    with db.transact() as cursor:
        cursor.execute("SELECT * FROM general_log")
    assert db.num_log_events() == BASELINE_NUM_EVENTS + 3

    db.clear_logs()
    assert db.num_log_events() == BASELINE_NUM_EVENTS + 1

def test_get_general_log_events(db):
    num_queries = 3
    queries = ["SELECT {:d}".format(i) for i in range(num_queries)]
    with db.transact() as cursor:
        for query in queries:
            cursor.execute(query)
    since = datetime.fromtimestamp(0, timezone.utc)

    events = db.get_general_log_events(since)
    # TODO assert

def test_get_general_log_events_limit(db):
    with db.transact() as cursor:
        for i in range(6):
            cursor.execute("SELECT 1")
    since = datetime.fromtimestamp(0, timezone.utc)

    limit = 2
    events = db.get_general_log_events(since, limit=limit)
    assert len(events) == limit

def test_get_general_log_events_empty(db):
    since = datetime.fromtimestamp(0, timezone.utc)
    events = db.get_general_log_events(since)
    assert len(events) == BASELINE_NUM_EVENTS + 1
