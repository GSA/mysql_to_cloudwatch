import pytz
from . import time_helper


def enable_logs(db):
    with db.cursor() as cursor:
        cursor.execute("SET GLOBAL log_output = 'TABLE'")
        cursor.execute("SET GLOBAL general_log = 'ON'")
        db.commit()

def mysql_to_cw_log_event(row):
    event_time = row[0]
    cmd = row[1]
    query = row[2]

    # normalize data
    if not event_time.tzname():
        # assume UTC
        event_time = pytz.utc.localize(event_time)
    if hasattr(query, 'decode'):
        # convert from byte array
        query = query.decode()

    msg = cmd
    if query:
        msg += ': ' + query

    return {
        'timestamp': time_helper.datetime_to_ms_since_epoch(event_time),
        'message': msg
    }

def get_general_log_events(db, since):
    """Returns them in CloudWatch Logs format."""

    with db.cursor() as cursor:
        print("Retrieving events from MySQL since {}...".format(time_helper.datetime_str(since)))
        # TODO remove hack for only being able to upload < 10000 events at a time
        # http://stackoverflow.com/a/12125925/358804
        cursor.execute("""
            SELECT * FROM (
                SELECT event_time, command_type, argument
                FROM general_log
                WHERE event_time > %s
                #ORDER BY event_time DESC
                #LIMIT 1000
            ) sub
            ORDER BY event_time ASC
            """, (since,))

        events = map(mysql_to_cw_log_event, cursor)
        return list(events)

def rotate_general_logs_table(db):
    with db.cursor() as cursor:
        cursor.callproc("""rds_rotate_general_log""")
