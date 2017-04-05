from . import cloudwatch
from . import mysql


def set_up_logs(db, cw_client, group, stream):
    mysql.enable_logs(db)
    cloudwatch.create_log_group(cw_client, group)
    cloudwatch.create_log_stream(cw_client, group, stream)

def copy_general_logs(db, cw_client, group, stream, since, seq_token=None):
    events = mysql.get_general_log_events(db, since)
    cloudwatch.upload_logs(cw_client, group, stream, events, seq_token=seq_token)

def run(db, cw_client, group, stream):
    since = cloudwatch.get_latest_cw_event(cw_client, group, stream)
    seq_token = cloudwatch.get_seq_token(cw_client, group, stream)

    # TODO copy error log
    copy_general_logs(db, cw_client, group, stream, since, seq_token=seq_token)
