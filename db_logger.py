import psycopg2

from utils import current_time_in_milli


class DatabaseLogger:
    conn = None
    cursor = None

    def __init__(self, host, name, user, password):
        self.conn = psycopg2.connect(host=host, dbname=name, user=user, password=password)
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def log_chat(self, sender, message, channel, moderator, sub, badges, color, turbo):
        if not moderator:
            moderator = '0'
        if not sub:
            sub = '0'
        if not badges:
            badges = '0'
        if not color:
            color = '000000'
        if not turbo:
            turbo = '0'
        if len(message) > 512:
            message = message[:512]

        if self.cursor.closed:
            return

        try:
            self.cursor.execute("INSERT INTO chat_log (sender, message, channel, moderator, sub, badges, color, turbo, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (sender, message, channel, moderator, sub, badges, color, turbo, current_time_in_milli()))
        except psycopg2.DataError as e:
            print e
            print message

    def log_stream_stats(self, stream):
        if 'status' not in stream['channel']:
            stream['channel']['status'] = None
        elif stream['channel']['status'] and len(stream['channel']['status']) > 128:
            stream['channel']['status'] = stream['channel']['status'][:128]
        if 'game' not in stream['channel']:
            stream['channel']['game'] = None

        if self.cursor.closed:
            return

        self.cursor.execute("INSERT INTO stream_log (channel, title, game, viewers, date) "
                            "VALUES (%s, %s, %s, %s, %s)",
                            (stream['channel']['name'],
                             stream['channel']['status'],
                             stream['channel']['game'],
                             int(stream['viewers']),
                             current_time_in_milli()))
