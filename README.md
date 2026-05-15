# Discord Translate Bot

Discord bot for translating messages in explicitly configured channels.

## What It Does

- Translates only messages from channel IDs listed in `AUTO_TRANSLATE_CHANNELS`
- Does not translate anything when `AUTO_TRANSLATE_CHANNELS` is empty
- Uses DeepL first and falls back to LibreTranslate
- Supports reaction-based translation only in configured channels
- Sends translated results as Discord embeds

## Environment Variables

- `DISCORD_TOKEN` - token for your Discord bot
- `DEEPL_API_KEY` - API key for DeepL translation service
- `AUTO_TRANSLATE_CHANNELS` - comma-separated Discord channel IDs where translation is allowed
- `LIBRETRANSLATE_URL` - LibreTranslate endpoint, for example `http://localhost:5000/translate`

Create a local `.env` file from `.env.example` on the server. Do not commit real bot tokens or API keys.

Example:

```env
DISCORD_TOKEN=your_discord_bot_token
DEEPL_API_KEY=your_deepl_api_key
AUTO_TRANSLATE_CHANNELS=123456789012345678
LIBRETRANSLATE_URL=http://localhost:5000/translate
```

For multiple allowed channels:

```env
AUTO_TRANSLATE_CHANNELS=123456789012345678,987654321098765432
```

## Install

```bash
python3 -m pip install -r requirements.txt
```
