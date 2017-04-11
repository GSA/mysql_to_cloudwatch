import boto3
from botocore.stub import Stubber
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
def cw_client():
    return boto3.client('logs', region_name='us-east-1')

@pytest.fixture
def cw(cw_client):
    cw = cloudwatch.CloudWatch(cw_client, 'somegroup', 'somestream')
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
