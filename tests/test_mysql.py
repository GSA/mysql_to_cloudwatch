import datetime
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

def test_mysql_to_cw_log_event():
    row = [
        datetime.datetime.utcfromtimestamp(1000),
        'Query',
        'SELECT * FROM sometable'.encode()
    ]
    result = mysql.mysql_to_cw_log_event(row)
    assert result == {
        'timestamp': 1000000,
        'message': 'Query: SELECT * FROM sometable'
    }

def test_clear_logs(conn, db):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM general_log")
        conn.commit()
    assert db.num_log_events() == BASELINE_NUM_EVENTS + 3

    db.clear_logs()
    assert db.num_log_events() == BASELINE_NUM_EVENTS + 1

def test_get_general_log_events(conn, db):
    num_queries = 3
    queries = ["SELECT {:d}".format(i) for i in range(num_queries)]
    with conn.cursor() as cursor:
        for query in queries:
            cursor.execute(query)
        conn.commit()
    since = datetime.datetime.utcfromtimestamp(0)

    events = db.get_general_log_events(since)

    for i in range(num_queries):
        event = events[BASELINE_NUM_EVENTS + i]
        actual = event['message']
        expected = "Query: {}".format(queries[i])
        assert actual == expected

def test_get_general_log_events_empty(db):
    since = datetime.datetime.utcfromtimestamp(0)
    events = db.get_general_log_events(since)
    assert len(events) == BASELINE_NUM_EVENTS + 1
