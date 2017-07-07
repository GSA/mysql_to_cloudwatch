import pymysql
import pytz
import sys
from contextlib import contextmanager
from . import time_helper


def mysql_to_cw_log_event(row):
    event_time = row[0]
    cmd = row[1]
    query = row[2]

    # normalize data - seems to be inconsistent coming from MySQL
    if hasattr(query, 'decode'):
        # convert from byte array
        query = query.decode()

    if not event_time.tzname():
        # assume UTC
        event_time = pytz.utc.localize(event_time)

    msg = cmd
    if query:
        msg += ': ' + query

    return {
        'timestamp': time_helper.datetime_to_ms_since_epoch(event_time),
        'message': msg
    }

class MySQL:
    def __init__(self, conn):
        self.conn = conn

    @contextmanager
    def transact(self):
        """Run a block within a transaction."""

        with self.conn.cursor() as cursor:
            yield cursor
            self.conn.commit()

    def get_global(self, cursor, var):
        # "This statement does not require any privilege", so no need to handle permissions issues.
        # https://dev.mysql.com/doc/refman/5.7/en/show-variables.html
        cursor.execute("SELECT @@GLOBAL.%s", (var,))
        return cursor.fetchone()[0]

    def set_global(self, cursor, var, val, alt_value=None):
        current = self.get_global(cursor, var)
        if current == val or (alt_value and current == alt_value):
            print("{} already set to {}.".format(var, val))
        else:
            print("Setting {}={}...".format(var, val))
            try:
                # http://stackoverflow.com/a/10077141/358804
                cursor.execute("SET GLOBAL {} = {}".format(var, val))
            except pymysql.err.DatabaseError as err:
                code = err.args[0]
                if code == pymysql.constants.ER.SPECIFIC_ACCESS_DENIED_ERROR:
                    print("Unable to set {}={} in MySQL - you will need to do so externally.".format(var, val), file=sys.stderr)
                else:
                    raise

    def enable_logs(self):
        with self.transact() as cursor:
            self.set_global(cursor, 'log_output', 'TABLE')
            self.set_global(cursor, 'general_log', 'ON', alt_value=1)

    def clear_logs(self):
        with self.transact() as cursor:
            # http://stackoverflow.com/a/12247102/358804
            cursor.execute("TRUNCATE TABLE general_log")

    def num_log_events(self):
        with self.transact() as cursor:
            cursor.execute("SELECT COUNT(*) FROM general_log")
            return cursor.fetchone()[0]

    def get_general_log_events(self, since, limit=1000):
        """Returns them in CloudWatch Logs format."""

        with self.transact() as cursor:
            print("Retrieving events from MySQL since {}...".format(time_helper.datetime_str(since)))
            # TODO remove hack for only being able to upload < 10000 events at a time
            # http://stackoverflow.com/a/12125925/358804
            cursor.execute("""
                SELECT * FROM (
                    SELECT event_time, command_type, argument
                    FROM general_log
                    WHERE event_time > %s
                    ORDER BY event_time DESC
                    LIMIT %s
                ) sub
                ORDER BY event_time ASC
                """, (since, limit,))

            events = map(mysql_to_cw_log_event, cursor)
            return list(events)
