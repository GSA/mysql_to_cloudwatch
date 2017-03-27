import datetime


def create_log_group(client, name):
    response = client.describe_log_groups(logGroupNamePrefix=name)
    if response['logGroups']:
        print("Log group exists.")
    else:
        print("Creating log group...")
        client.create_log_group(logGroupName=name)

def get_log_stream(client, group, stream):
    response = client.describe_log_streams(
        logGroupName=group,
        logStreamNamePrefix=stream
    )
    # http://stackoverflow.com/a/365934/358804
    return next(iter(response['logStreams']), None)

def create_log_stream(client, group, stream):
    log_stream = get_log_stream(client, group, stream)
    if log_stream:
        print("Log stream exists.")
    else:
        print("Creating log stream...")
        client.create_log_stream(
            logGroupName=group,
            logStreamName=stream
        )

def get_latest_cw_event(cw_client, group, stream):
    cw_events = cw_client.get_log_events(
        logGroupName=group,
        logStreamName=stream,
        startFromHead=False,
        limit=1
    )

    if cw_events['events']:
        latest_event = cw_events['events'][0]
        timestamp = latest_event['timestamp'] / 1000
    else:
        # no previous event - query since the epoch
        timestamp = 0

    return datetime.datetime.utcfromtimestamp(timestamp)

def upload_logs(cw_client, group, stream, events, seq_token=None):
    print("Uploading {:d} events...".format(len(events)))

    # http://stackoverflow.com/a/8686243/358804
    log_args = {
        'logGroupName': group,
        'logStreamName': stream,
        'logEvents': events
    }
    if seq_token:
        log_args['sequenceToken'] = seq_token

    cw_client.put_log_events(**log_args)

def get_seq_token(cw_client, group, stream):
    log_stream = get_log_stream(cw_client, group, stream)
    return log_stream.get('uploadSequenceToken', None)
