## [Python 3] Discord Bot & Webhook
Discord bot that provides services related to [Star Citizen](https://robertsspaceindustries.com) and a webhook to
automate parsing and sending of update info on the public roadmap every friday.

DISCLAIMER: This repository was made for personal/portfolio use and not meant to be open source, but can be run with 
slight modification.

### Features
1. Schedule an event and have it post in a chat when it is near event time. [Bot][WIP/Discontinued to focus on roadmap features]
2. Fleet manager - List user(s) ship list and add/remove from the list. [Bot]
3. Roadmap - Get data on each upcoming patch's features and update information from last update. [Bot/Webhook]

### Setup
1. Clone repository
2. Create tokens.yaml in root directory with following information:
```yaml
bot_token: "Client Secret - Create an application on https://discordapp.com/developers/applications/"
test_channel: "Discord test channel in lamba_function.py"
```
3. Create webhooks.yaml in root directory with following information if using webhooks:
```yaml
- guild_id: "Guild ID received from webhook"
  webhook_token: "Token from webhook"
  webhook_id: "ID from webhook"
```

### Run
- To run bot simply run `python3 bot.py` in root directory on command line. (Blocks further command line entry whiel bot
is running)

- Discord webhook is not meant to be publicly ran, to gather update data, it needs to be run for at least 2 weeks to
gather data and change the s3 bucket.