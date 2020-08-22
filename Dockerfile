FROM python:3-alpine

RUN apk --no-cache add tzdata gcc libc-dev && \
    addgroup -g 6697 -S irc-bot && \
    adduser -u 6697 -S irc-bot -G irc-bot && \
    mkdir /irc-bot && \
    mkdir /irc-bot/data && \
    chown -R 6697:6697 /irc-bot/data

WORKDIR /irc-bot

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt && apk del gcc libc-dev && chown -R 6697:6697 /irc-bot

COPY . .

USER irc-bot

VOLUME /irc-bot/data

ENTRYPOINT ["python3", "-m", "bot.main"]
