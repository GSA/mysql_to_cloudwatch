from contextlib import contextmanager


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

class MySQL:
    def __init__(self, conn):
        self.conn = conn

    @contextmanager
    def transact(self):
        """Run a block within a transaction."""

        with self.conn.cursor() as cursor:
            yield cursor
            self.conn.commit()

    def enable_logs(self):
        with self.transact() as cursor:
            cursor.execute("SET GLOBAL log_output = 'TABLE'")
            cursor.execute("SET GLOBAL general_log = 'ON'")

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
            print("Retrieving events since {:%Y-%m-%d %H:%M:%S}...".format(since))
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
