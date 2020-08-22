# IRC Reminder Bot
### A Dockerized IRC Reminder Bot written in Python 3
***

### Setting up

##### Quickstart

```shell
# Clone the repository
git clone https://github.com/AlexGustafsson/irc-reminder-bot
# Enter the directory
cd irc-reminder-bot
# Run
python3 -m bot.main --server irc.example.com
```

You can also run the container using Docker, like so:

```shell
# Build the image
docker build -t axgn/irc-reminder-bot:latest .

# Run
docker run -v data:/irc-bot/data axgn/irc-reminder-bot --server irc.example.com --channel "#random"
```

### Documentation

#### Running with Docker

```shell
docker run axgn/irc-emoji-bot --server irc.example.com --channel "#random"
```

The image can be run stateless and based on Alpine and is roughly 98MB in size. While running, the container usually uses 0% of the CPU and roughly 15MB of RAM. During load it uses about 0.20% CPU and while starting about 1.5% on a single core and an unchanged amount of RAM.

To prevent any unforseen events, one can therefore limit the container's resources by using the flags `--cpus=0.05` and `--memory=50MB` which should both leave some head room.

#### Invoking via IRC

To see help messages send `reminder-bot: help` in the channel where the bot lives.

To create a reminder send `RemindMe! 2 days` in a channel where the bot exists. You can also specify a text by sending `RemindMe! 2 days "Discover a cure for cancer"`.

#### Known issues

The parsing library `dateparser` seems to think that `5 seconds` is the same as `5 seconds ago`. Therefore one must explicitly write `in 5 seconds` instead.

### Contributing

Any contribution is welcome. If you're not able to code it yourself, perhaps someone else is - so post an issue if there's anything on your mind.

###### Development

Clone the repository:
```
git clone https://github.com/AlexGustafsson/irc-reminder-bot && cd irc-reminder-bot
```

### Disclaimer

_Although the project is very capable, it is not built with production in mind. Therefore there might be complications when trying to use the bot for large-scale projects meant for the public. The bot was created to easily create reminders in IRC channels and as such it might not promote best practices nor be performant._
