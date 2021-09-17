## Overheard at SHAD

### Introduction

A Telegram bot for anonymous submissions, which are then reviewed by moderators and published in a Telegram channel. It is hoped that it will enrich social life at Yandex's School of Data Analysis (a.k.a. [SHAD](https://yandexdataschool.com)).

The idea for it comes from the University of Cambridge's [Camfess](https://www.facebook.com/pg/camfession/posts/?ref=page_internal).  The process is as follows:

1. The bot prompts a user to submit a post, which can be anything from a humorous anecdote to a love confession.
2. The post is anonymously shared with a group of moderators
3. If the post is approved, it will be published in a linked Telegram channel.

### Deployment

The app is packaged in a Docker container and needs three environmental variables to run

* `TOKEN` – Telegram's bot access token
* `MOD_CHAT_ID` – the numertical id of the moderators' chat (where the bot must have been added)
* `CHANNEL_ID` – the numertical id of the channel where submissions will be posted (where the bot must have been added)

You can write these to a `.env` file or specify in a command-line argument. What's left is start the service via `docker-compose`
 
```bash
docker compose up
```

### Examples

You can check out the bot's functionality at <https://t.me/overheard_at_shad>.