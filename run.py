import boto3
# http://mysqlclient.readthedocs.io/en/latest/user_guide.html#mysqldb
import MySQLdb
import os
from src import cloudwatch
from src import env_helper
from src import mysql


DB_KWARGS = env_helper.get_db_kwargs(os.environ)
LOG_GROUP_NAME = os.environ['LOG_GROUP_NAME']
LOG_STREAM_NAME = os.environ.get('LOG_STREAM_NAME', DB_KWARGS['host'])


def test_setup(db, cw_client, group, stream):
    mysql.enable_logs(db)
    cloudwatch.create_log_group(cw_client, group)
    cloudwatch.create_log_stream(cw_client, group, stream)

def copy_general_logs(db, cw_client, group, stream, since, seq_token=None):
    events = mysql.get_general_log_events(db, since)
    cloudwatch.upload_logs(cw_client, group, stream, events, seq_token=seq_token)


if __name__ == '__main__':
    db = MySQLdb.connect(**DB_KWARGS)
    cw_client = boto3.client('logs')

    test_setup(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    since = cloudwatch.get_latest_cw_event(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)
    seq_token = cloudwatch.get_seq_token(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    # TODO copy error log
    copy_general_logs(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME, since, seq_token=seq_token)

    print("DONE")
