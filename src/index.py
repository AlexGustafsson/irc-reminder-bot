#!/usr/bin/env python3
import os
import re
import sys
import sqlite3
from datetime import datetime
from threading import Timer

import dateparser

from connector import IRC

dirname = os.path.dirname(__file__)

server = os.getenv('IRC_SERVER', None)
port = int(os.getenv('IRC_PORT', '6697'))
channel = os.getenv('IRC_CHANNEL', '#random')
nick = os.getenv('IRC_NICK', 'reminder-bot')
user = os.getenv('IRC_USER', 'reminder-bot')
gecos = os.getenv('IRC_GECOS', 'Reminder Bot v0.0.3 (github.com/AlexGustafsson/irc-reminder-bot)')
timezone = os.getenv('TZ', 'Europe/Stockholm')
data_directory = os.getenv('DATA_DIRECTORY', '.')
data_file = '{0}/reminders.sqlite'.format(data_directory)

timer = None


def prettyTimestamp(timestamp):
    # Calculate the current local time
    return datetime.fromtimestamp(timestamp).astimezone().strftime('%Y-%m-%d %H:%M:%S')


def setup_database():
    database = sqlite3.connect(data_file)
    cursor = database.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS Reminders (author TEXT, deadline INTEGER, channel TEXT, body TEXT);'
    cursor.execute(sql)
    database.commit()
    database.close()


def create_reminder(author, deadline, channel, body):
    database = sqlite3.connect(data_file)
    sql = 'INSERT INTO Reminders (author, deadline, channel, body) VALUES (?,?,?,?)'
    cursor = database.cursor()
    cursor.execute(sql, (author, deadline, channel, body))
    database.commit()
    database.close()


def get_reminders():
    database = sqlite3.connect(data_file)
    database.row_factory = sqlite3.Row
    sql = 'SELECT * FROM Reminders ORDER BY deadline ASC'
    cursor = database.cursor()
    cursor.execute(sql)
    rows = [dict(row) for row in cursor.fetchall()]
    database.close()

    return rows


def remove_reminder(deadline):
    database = sqlite3.connect(data_file)
    sql = 'DELETE FROM Reminders WHERE deadline = ?'
    cursor = database.cursor()
    cursor.execute(sql, (deadline,))
    database.commit()
    database.close()


def set_timer():
    global timer

    reminders = get_reminders()
    if len(reminders) == 0:
        return

    next_reminder = reminders[0]
    if timer is not None:
        timer.cancel()
        timer = None

    now = datetime.timestamp(datetime.now())
    delay = max(next_reminder['deadline'] - now, 0)

    print('Bot: Setting timer for {0} seconds ({1})'.format(delay, prettyTimestamp(next_reminder['deadline'])))
    timer = Timer(delay, handle_timer, [next_reminder])
    timer.start()


def handle_timer(reminder):
    print('Bot: Handling reminder', reminder['deadline'], '({0})'.format(prettyTimestamp(reminder['deadline'])))
    message = 'Reminding {0}'.format(reminder['author'])
    if reminder['body'] is not None:
        message += ': {0}'.format(reminder['body'])

    irc.sendAction(reminder['channel'], message)
    remove_reminder(reminder['deadline'])
    set_timer()


def handle_help():
    irc.send(channel, 'I handle reminders for users and channels.')
    irc.send(channel, 'You can use the following commands:')
    irc.send(channel, 'RemindMe! in 1 hour "That was easy!"')
    irc.send(channel, 'RemindMe! January 19, 2038, at 03:14:08 UTC "Did we make it?"')
    irc.send(channel, '{0}: help'.format(nick))


def handle_reminder(author, channel, message):
    match = re.match('([^"”]*)(["”].*["”])?', message)
    if match is None:
        return

    notification_time = match.group(1)
    notification_body = match.group(2)[1:-1] if match.group(2) is not None else None

    parsed_date = dateparser.parse(notification_time, settings={
        'TIMEZONE': timezone
    })

    if parsed_date is None:
        irc.send(channel, '{0}: Sorry, I didn\'t quite get that'.format(author))
        return

    deadline = round(datetime.timestamp(parsed_date))

    try:
        create_reminder(author, deadline, channel, notification_body)
        set_timer()

        irc.send(channel, 'A reminder has been set for {0}'.format(prettyTimestamp(deadline)))
    except Exception as e:
        irc.send(channel, 'Could not set notfication')
        print(e)


def handle_message(message):
    sender, type, target, body = message
    if type == 'PRIVMSG':
        if body == '{0}: help'.format(nick):
            handle_help()
        elif body.find('RemindMe! ') == 0:
            # Handle direct messages
            if target == nick:
                target = sender
            handle_reminder(sender, target, body[10:])


if server is None:
    print('Cannot start the bot without a given server')
    sys.exit()

print('Bot: Connecting to {0}:{1} as {2} ({3})'.format(server, port, user, nick))
irc = IRC()
irc.connect(server, port, user, nick, gecos)
print('Bot: Connected to {0}'.format(server))

print('Bot: Joining channel {0}'.format(channel))
irc.join(channel)

setup_database()
set_timer()

print('Bot: Starting event loop')
while True:
    message = irc.retrieveMessage()
    handle_message(message)
