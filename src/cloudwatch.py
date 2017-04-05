import datetime


class CloudWatch:
    def __init__(self, client, group, stream):
        self.client = client
        self.group = group
        self.stream = stream

    def create_log_group(self):
        response = self.client.describe_log_groups(logGroupNamePrefix=self.group)
        if response['logGroups']:
            print("Log group exists.")
        else:
            print("Creating log group...")
            self.client.create_log_group(logGroupName=self.group)

    def get_log_stream(self):
        response = self.client.describe_log_streams(
            logGroupName=self.group,
            logStreamNamePrefix=self.stream
        )
        # http://stackoverflow.com/a/365934/358804
        return next(iter(response['logStreams']), None)

    def create_log_stream(self):
        log_stream = self.get_log_stream()
        if log_stream:
            print("Log stream exists.")
        else:
            print("Creating log stream...")
            self.client.create_log_stream(
                logGroupName=self.group,
                logStreamName=self.stream
            )

    def get_latest_cw_event(self):
        events = self.client.get_log_events(
            logGroupName=self.group,
            logStreamName=self.stream,
            startFromHead=False,
            limit=1
        )

        if events['events']:
            latest_event = events['events'][0]
            timestamp = latest_event['timestamp'] / 1000
        else:
            # no previous event - query since the epoch
            timestamp = 0

        return datetime.datetime.utcfromtimestamp(timestamp)

    def upload_logs(self, events):
        print("Uploading {:d} events...".format(len(events)))

        # http://stackoverflow.com/a/8686243/358804
        log_args = {
            'logGroupName': self.group,
            'logStreamName': self.stream,
            'logEvents': events
        }
        seq_token = self.get_seq_token()
        if seq_token:
            log_args['sequenceToken'] = seq_token

        self.client.put_log_events(**log_args)

    def get_seq_token(self):
        log_stream = self.get_log_stream()
        return log_stream.get('uploadSequenceToken', None)
