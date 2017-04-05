import boto3
# https://pymysql.readthedocs.io/en/latest/
import pymysql
import os
import socket
from src import env_helper
from src import integration
from src import mysql


DB_KWARGS = env_helper.get_db_kwargs(os.environ)
# default to the hostname of the current machine
DB_HOST = DB_KWARGS.get('host', socket.gethostname())
LOG_GROUP_NAME = os.environ['LOG_GROUP_NAME']
LOG_STREAM_NAME = os.environ.get('LOG_STREAM_NAME', DB_HOST)


if __name__ == '__main__':
    conn = pymysql.connect(**DB_KWARGS)
    db = mysql.MySQL(conn)
    cw_client = boto3.client('logs')

    integration.set_up_logs(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)
    integration.run(db, cw_client, LOG_GROUP_NAME, LOG_STREAM_NAME)

    print("DONE")
