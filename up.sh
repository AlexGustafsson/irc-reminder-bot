#!/usr/bin/env bash

# Please see the README for more information
docker run \
  --env IRC_SERVER='irc.example.org' \
  --env IRC_PORT='6697' \
  --env IRC_CHANNEL='#random' \
  --env IRC_NICK='reminder-bot' \
  --env IRC_USER='reminder-bot' \
  --env IRC_GECOS='Reminder Bot v0.0.2 (github.com/AlexGustafsson/irc-reminder-bot)' \
  --env TIMEZONE='CET' \
  --name irc-reminder-bot \
  --detach \
  --restart always \
  --cpus=0.05 \
  --memory=50MB \
  -v irc-reminder-bot:/var/data \
  axgn/irc-reminder-bot
