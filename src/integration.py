def set_up_logs(db, cw):
    db.enable_logs()
    cw.create_log_group()
    cw.create_log_stream()

def copy_general_logs(db, cw, since, seq_token=None):
    events = db.get_general_log_events(since)
    cw.upload_logs(events, seq_token=seq_token)

def run(db, cw):
    since = cw.get_latest_cw_event()
    seq_token = cw.get_seq_token()

    # TODO copy error log
    copy_general_logs(db, cw, since, seq_token=seq_token)
