import boto3
import datetime
# http://mysqlclient.readthedocs.io/en/latest/user_guide.html#mysqldb
import MySQLdb


DB_HOST = "mysql"
LOG_GROUP_NAME = "mysql_to_cloudwatch-test"
LOG_STREAM_NAME = DB_HOST


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

def test_setup(db, cw_client, group, stream):
    with db as cursor:
        cursor.execute("SET GLOBAL log_output = 'TABLE'")
        cursor.execute("SET GLOBAL general_log = 'ON'")
        db.commit()

    create_log_group(cw_client, group)
    create_log_stream(cw_client, group, stream)

def datetime_to_ms_since_epoch(dt):
    return int(dt.timestamp() * 1000.0)

def mysql_to_cw_log_event(row):
    event_time = row[0]
    cmd = row[1]
    query = row[2].decode("utf-8")
    msg = cmd
    if query:
        msg += ': ' + query

    return {
        'timestamp': datetime_to_ms_since_epoch(event_time),
        'message': msg
    }

def copy_general_logs(db, cw_client, group, stream, since, seq_token=None):
    with db as cursor:
        print("Retrieving events since {:%Y-%m-%d %H:%M}...".format(since))
        cursor.execute("""
            SELECT event_time, command_type, argument
            FROM general_log
            WHERE event_time > %s
            """, (since,))
        events = list(map(mysql_to_cw_log_event, cursor))
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


if __name__ == '__main__':
    db = MySQLdb.connect(host=DB_HOST, db="mysql")
    cw_client = boto3.client('logs')

    test_setup(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    log_stream = get_log_stream(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)
    print(log_stream)
    # fall back to epoch
    timestamp = log_stream.get('lastEventTimestamp', 0) / 1000
    since = datetime.datetime.utcfromtimestamp(timestamp)
    seq_token = log_stream.get('uploadSequenceToken', None)

    # TODO copy error log
    copy_general_logs(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME, since, seq_token=seq_token)

    print("DONE")
