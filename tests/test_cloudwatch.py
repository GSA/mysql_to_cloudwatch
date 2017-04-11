import boto3
from botocore.stub import Stubber
from doubles import expect
import pytest
from ..src import cloudwatch

@pytest.fixture
def client():
    return boto3.client('logs', region_name='us-east-1')

@pytest.fixture
def cw(client):
    return cloudwatch.CloudWatch(client, 'somegroup', 'somestream')

# TODO test_create_log_group_present

# TODO test_create_log_group_empty

# TODO test_get_log_stream_present

# TODO test_get_log_stream_empty

# TODO test_create_log_stream_present

# TODO test_create_log_stream_empty

def test_upload_logs_without_seq_token(client, cw):
    events = [
        {
            'timestamp': 1000,
            'message': 'foo'
        }
    ]

    stubber = Stubber(client)
    response = {}
    expected_params = {
        'logGroupName': 'somegroup',
        'logStreamName': 'somestream',
        'logEvents': events
    }

    stubber.add_response('put_log_events', response, expected_params)
    stubber.activate()

    expect(cw).get_seq_token.and_return(None)

    cw.upload_logs(events)

def test_upload_logs_with_no_events(client, cw):
    expect(cw).get_seq_token.never()
    expect(client).put_log_events.never()

    cw.upload_logs([])

# TODO test_upload_logs_with_seq_token
