# Mubert_bot
### Telegram bot for music generation via [mubert.com](mubert.com) api
___

based on https://github.com/MubertAI/Mubert-Text-to-Music
___
### Installation

1. Get api key from [@BotFather](t.me/BotFather) in telegram
2. Insert ___telegram api key___ and your ___email___ in `docker-compose.yaml`
3. install docker and docker-compose
4. run
    ```bash
    docker-compose up -d -f ./docker-compose.yaml
    ```
___
### Usage
- Just simply send some music tags or music description to bot.

- To change music track length type desired length `=300` for 300 seconds or `+5` to increase it for 5 seconds or `-30` for decreasing track length.

- For changing __loop_mode__ use `/loop` command
___
### Personal data
- bot uses local sqlite database to store __hashed user id__, __track_length__ and __track_mode__.

- __hashed id__ its a function of (telegram_id + telegram_user_names).