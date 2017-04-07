def set_up_logs(db, cw):
    db.enable_logs()
    cw.create_log_group()
    cw.create_log_stream()

def get_new_db_events(db, cw):
    since = cw.get_latest_cw_event()
    return db.get_general_log_events(since)

def copy_new_general_logs(db, cw):
    events = get_new_db_events(db, cw)
    # CloudWatch Logs complains if trying to send zero events
    # http://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html#CWL-PutLogEvents-request-logEvents
    if events:
        cw.upload_logs(events)

def run(db, cw):
    # TODO copy error log
    copy_new_general_logs(db, cw)
