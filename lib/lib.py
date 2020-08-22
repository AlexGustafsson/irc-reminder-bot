import re
import sqlite3
from datetime import datetime
from threading import Timer
import logging

import pytz
import dateparser

logger = logging.getLogger(__name__)
timer = None
database_file = None


def prettyTimestamp(timestamp, timezone):
    # Calculate the current local time
    return datetime.fromtimestamp(timestamp).astimezone(pytz.timezone(timezone)).strftime('%Y-%m-%d %H:%M:%S')


def setup_database(file):
    global database_file
    database_file = file
    database = sqlite3.connect(database_file)
    cursor = database.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS Reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, deadline INTEGER, target TEXT, body TEXT)'
    logger.info("Setting up database")
    cursor.execute(sql)
    database.commit()
    database.close()


def create_reminder(author, deadline, target, body):
    sql = 'INSERT INTO Reminders (author, deadline, target, body) VALUES (?,?,?,?)'
    database = sqlite3.connect(database_file)
    cursor = database.cursor()
    logger.info("Creating reminder")
    cursor.execute(sql, (author, deadline, target, body))
    database.commit()
    database.close()


def get_reminders():
    database = sqlite3.connect(database_file)
    database.row_factory = sqlite3.Row
    sql = 'SELECT * FROM Reminders ORDER BY deadline ASC'
    cursor = database.cursor()
    logger.info("Getting reminders")
    cursor.execute(sql)
    rows = [dict(row) for row in cursor.fetchall()]
    database.close()

    return rows


def remove_reminder(reminder):
    database = sqlite3.connect(database_file)
    sql = 'DELETE FROM Reminders WHERE id = ?'
    cursor = database.cursor()
    logger.info("Removing reminder")
    cursor.execute(sql, (reminder["id"],))
    database.commit()
    database.close()


def set_timer(irc, timezone):
    global timer

    reminders = get_reminders()
    if len(reminders) == 0:
        return

    next_reminder = reminders[0]
    if timer is not None:
        timer.cancel()
        timer = None

    now = datetime.timestamp(datetime.now(tz=pytz.timezone(timezone)))
    delay = max(next_reminder["deadline"] - now, 0)
    logger.info("Next event is at %d (in %ds)", next_reminder["deadline"], delay)

    timer = Timer(delay, handle_timer, [irc, timezone, next_reminder])
    timer.start()
    logger.info("Setting timer for %ds", delay)


def handle_timer(irc, timezone, reminder):
    message = "Reminding {0}".format(reminder["author"])
    if reminder["body"] is not None:
        message += ": {0}".format(reminder["body"])

    irc.send_notice(reminder["target"], message)
    remove_reminder(reminder)
    set_timer(irc, timezone)


def handle_help(irc, target, nick):
    irc.send_message(target, "I handle reminders for users and channels.")
    irc.send_message(target, "You can use the following commands:")
    irc.send_message(target, "RemindMe! in 1 hour \"That was easy!\"")
    irc.send_message(target, "RemindMe! January 19, 2038, at 03:14:08 UTC \"Did we make it?\"")
    irc.send_message(target, "{}: help".format(nick))


def handle_reminder(irc, timezone, author, target, message):
    match = re.match("([^\"”]*)([\"”].*[\"”])?", message)
    if match is None:
        return

    notification_time = match.group(1)
    notification_body = match.group(2)[1:-1] if match.group(2) is not None else None

    parsed_date = dateparser.parse(notification_time, settings={
        "TIMEZONE": timezone
    })

    if parsed_date is None:
        irc.send_message(target, "{}: Sorry, I didn't quite get that".format(author))
        return
    # Localize as necessary
    if parsed_date.tzinfo is None or parsed_date.tzinfo.utcoffset(parsed_date) is None:
        parsed_date = pytz.timezone(timezone).localize(parsed_date)

    deadline = round(datetime.timestamp(parsed_date))

    try:
        create_reminder(author, deadline, target, notification_body)
        irc.send_message(target, "A reminder has been set for {}".format(prettyTimestamp(deadline, timezone)))
        set_timer(irc, timezone)
    except Exception as exception:
        irc.send_message(target, "Could not set notfication")
        logger.error("Unable to set notification", exc_info=True)
