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


db = MySQLdb.connect(host=DB_HOST, db="mysql")

# TODO fetch error log

with db as cursor:
    cursor.execute("SET GLOBAL log_output = 'TABLE'")
    cursor.execute("SET GLOBAL general_log = 'ON'")
    db.commit()

with db as cursor:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        print(table_name)

cw_client = boto3.client('logs')
create_log_group(cw_client, LOG_GROUP_NAME)
create_log_stream(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

with db as cursor:
    # TODO select since last time
    cursor.execute("SELECT * FROM general_log")
    for row in cursor:
        print(row)

print("DONE")
