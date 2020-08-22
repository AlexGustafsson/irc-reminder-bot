import csv
import logging
import random
import re
from argparse import ArgumentParser
from os import path

from irc import IRC
from irc.messages import IRCMessage

import lib

def main() -> None:
    """Main entrypoint of the bot."""
    # Configure the default logging format
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)-5s] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create an argument parser for parsing CLI arguments
    parser = ArgumentParser(description="An IRC bot providing reminders")

    # Add parameters for the server connection
    parser.add_argument("-s", "--server", required=True, type=str, help="The server to connect to")
    # Add optional parameters for the server connection
    parser.add_argument("-p", "--port", default=6697, type=int, help="The port to connect to")
    parser.add_argument("--use-tls", default=True, type=bool, help="Whether or not to use TLS")
    parser.add_argument("-t", "--timeout", default=300, type=float, help="Connection timeout in seconds")

    # Add optional parameters for authentication etc.
    parser.add_argument("-u", "--user", default="reminder-bot", help="Username to use when connecting to the IRC server")
    parser.add_argument("-n", "--nick", default="reminder-bot", help="Nick to use when connecting to the IRC server")
    parser.add_argument("-g", "--gecos", default="Reminder Bot v1.0.0 (github.com/AlexGustafsson/irc-reminder-bot)", help="Gecos to use when connecting to the IRC server")
    parser.add_argument("-c", "--channel", required=True, action='append', help="Channel to join. May be used more than once")
    parser.add_argument("--timezone", required=False, default="Europe/Stockholm", help="Timezone for reminders")
    parser.add_argument("-f", "--file", required=False, default="data/reminders.sqlite", help="The reminders database file")

    # Parse the arguments
    options = parser.parse_args()

    # Create an IRC connection
    irc = IRC(
        options.server,
        options.port,
        options.user,
        options.nick,
        timeout=options.timeout,
        use_tls=options.use_tls
    )

    lib.setup_database(options.file)

    irc.connect()

    # Connect to specified channels
    for channel in options.channel:
        irc.join(channel)

    lib.set_timer(irc, options.timezone)

    # Handle all messages
    for message in irc.messages:
        if not isinstance(message, IRCMessage):
            continue

        target = message.author if message.target == options.nick else message.target

        if message.message == "{}: help".format(options.nick):
            lib.handle_help(irc, target, options.nick)
        elif message.message.find("RemindMe! ") == 0:
            lib.handle_reminder(irc, options.timezone, message.author, target, message.message[10:])


if __name__ == "__main__":
    main()
