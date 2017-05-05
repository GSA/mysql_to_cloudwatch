import boto3
# https://pymysql.readthedocs.io/en/latest/
import pymysql
import os
import socket
import sys
import traceback
from src import cloudwatch
from src import env_helper
from src import mysql
from src import time_helper


DB_KWARGS = env_helper.get_db_kwargs(os.environ)
# default to the hostname of the current machine
DB_HOST = DB_KWARGS.get('host', socket.gethostname())
LOG_GROUP_NAME = os.environ['LOG_GROUP_NAME']
LOG_STREAM_NAME = os.environ.get('LOG_STREAM_NAME', DB_HOST)


def test_setup(db, cw_client, group, stream):
    # mysql.enable_logs(db)
    cloudwatch.create_log_group(cw_client, group)
    cloudwatch.create_log_stream(cw_client, group, stream)

def copy_general_logs(db, cw_client, group, stream, since, seq_token=None):
    events = mysql.get_general_log_events(db, since)
    # CloudWatch Logs complains if trying to send zero events
    if events:
        mysql.rotate_general_logs_table(db)
        submit_events_to_cloudwatch(events, cw_client, group, stream)

def submit_events_to_cloudwatch(events, cw_client, group, stream, chunk_size=500):
   if events:
        for chunk in [events[i:i + chunk_size] for i in range(0, len(events), chunk_size)]:
               seq_token = cloudwatch.get_seq_token(cw_client, group, stream)
               try:
                     cloudwatch.upload_logs(cw_client, group, stream, chunk, seq_token=seq_token)
               except:
                     if chunk_size == 1:
                           print('Ignoring exception: ', traceback.format_exc())
                     else:
                           submit_events_to_cloudwatch(chunk, group, stream, int(chunk_size/2)) 
        
def run(db, cw_client, group, stream):
    since = cloudwatch.get_latest_cw_event(cw_client, group, stream)
    time_helper.validate_time_zone(since)
    #seq_token = cloudwatch.get_seq_token(cw_client, group, stream)

    # TODO copy error log
    copy_general_logs(db, cw_client, group, stream, since)


if __name__ == '__main__':
    db = pymysql.connect(**DB_KWARGS)
    cw_client = boto3.client('logs')

    test_setup(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)
    run(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    print("DONE")
