def enable_logs(db):
    with db.cursor() as cursor:
        cursor.execute("SET GLOBAL log_output = 'TABLE'")
        cursor.execute("SET GLOBAL general_log = 'ON'")
        db.commit()

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

def get_general_log_events(db, since):
    """Returns them in CloudWatch Logs format."""

    with db.cursor() as cursor:
        print("Retrieving events since {:%Y-%m-%d %H:%M:%S}...".format(since))
        cursor.execute("""
            SELECT event_time, command_type, argument
            FROM general_log
            WHERE event_time > %s
            """, (since,))

        events = map(mysql_to_cw_log_event, cursor)
        return list(events)
