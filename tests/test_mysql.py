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
    since = datetime.datetime.utcfromtimestamp(0)

    events = db.get_general_log_events(since)

def test_get_general_log_events_limit(db):
    with db.transact() as cursor:
        for i in range(6):
            cursor.execute("SELECT 1")
    since = datetime.datetime.utcfromtimestamp(0)

    limit = 2
    events = db.get_general_log_events(since, limit=limit)
    assert len(events) == limit

def test_get_general_log_events_empty(db):
    since = datetime.datetime.utcfromtimestamp(0)
    events = db.get_general_log_events(since)
    assert len(events) == BASELINE_NUM_EVENTS + 1
