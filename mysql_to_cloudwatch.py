import boto3
# http://mysqlclient.readthedocs.io/en/latest/user_guide.html#mysqldb
import MySQLdb
from src import cloudwatch
from src import mysql


DB_HOST = "mysql"
LOG_GROUP_NAME = "mysql_to_cloudwatch-test"
LOG_STREAM_NAME = DB_HOST


def test_setup(db, cw_client, group, stream):
    mysql.enable_logs(db)
    cloudwatch.create_log_group(cw_client, group)
    cloudwatch.create_log_stream(cw_client, group, stream)

def copy_general_logs(db, cw_client, group, stream, since, seq_token=None):
    events = mysql.get_general_log_events(db, since)
    cloudwatch.upload_logs(cw_client, group, stream, events, seq_token=seq_token)


if __name__ == '__main__':
    db = MySQLdb.connect(host=DB_HOST, db="mysql")
    cw_client = boto3.client('logs')

    test_setup(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    since = cloudwatch.get_latest_cw_event(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)
    seq_token = cloudwatch.get_seq_token(cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    # TODO copy error log
    copy_general_logs(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME, since, seq_token=seq_token)

    print("DONE")
