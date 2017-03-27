import boto3
# http://mysqlclient.readthedocs.io/en/latest/user_guide.html#mysqldb
import MySQLdb

print("started")

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

def create_log_stream(client, group, stream):
    response = client.describe_log_streams(
        logGroupName=group,
        logStreamNamePrefix=stream
    )
    if response['logStreams']:
        print("Log stream exists.")
    else:
        print("Creating log stream...")
        client.create_log_stream(
            logGroupName=group,
            logStreamName=stream
        )

def datetime_to_ms_since_epoch(dt):
    return int(dt.timestamp() * 1000.0)

def mysql_to_cw_log_event(row):
    event_time = row[0]
    cmd = row[4]
    query = row[5].decode("utf-8")
    msg = cmd
    if query:
        msg += ': ' + query

    return {
        'timestamp': datetime_to_ms_since_epoch(event_time),
        'message': msg
    }


db = MySQLdb.connect(host=DB_HOST, db="mysql")

# TODO fetch error log

with db as cursor:
    cursor.execute("SET GLOBAL log_output = 'TABLE'")
    cursor.execute("SET GLOBAL general_log = 'ON'")
    db.commit()

cw_client = boto3.client('logs')
create_log_group(cw_client, LOG_GROUP_NAME)
create_log_stream(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

with db as cursor:
    # TODO select since last time
    cursor.execute("SELECT * FROM general_log")
    events = map(mysql_to_cw_log_event, cursor)

    cw_client.put_log_events(
        logGroupName=LOG_GROUP_NAME,
        logStreamName=LOG_STREAM_NAME,
        logEvents=list(events)
    )

print("DONE")
