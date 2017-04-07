from doubles import expect, ObjectDouble
import pytest
from ..src import cloudwatch
from ..src import integration
from ..src import mysql


@pytest.fixture
def db():
    conn = object()
    db = mysql.MySQL(conn)
    return ObjectDouble(db)

@pytest.fixture
def cw():
    client = object()
    cw = cloudwatch.CloudWatch(client, 'somegroup', 'somestream')
    return ObjectDouble(cw)

def test_copy_new_general_logs(db, cw):
    expect(cw).get_latest_cw_event.and_return(None)
    events = [
        {
            'time': 1000000,
            'message': 'foo'
        }
    ]
    expect(db).get_general_log_events.and_return(events)
    expect(cw).upload_logs.with_args(events)

    integration.copy_new_general_logs(db, cw)

def test_copy_new_general_logs_empty(db, cw):
    expect(cw).get_latest_cw_event.and_return(None)
    expect(db).get_general_log_events.and_return([])

    integration.copy_new_general_logs(db, cw)
