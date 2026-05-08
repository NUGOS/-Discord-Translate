# Discord Translate Bot

Python Discord bot experiment for translating messages into multiple languages.

This is a learning/automation project. It is not part of my main Java backend positioning, but it shows practical integration work with Discord, translation APIs, environment-based configuration, and async message handling.

## What It Does

- Reads Discord messages from configured channels
- Translates text into several target languages
- Uses DeepL first and falls back to LibreTranslate
- Supports reaction-based translation
- Sends translated results as Discord embeds

## Tech Stack

- Python
- discord.py
- aiohttp
- DeepL API
- LibreTranslate

## Environment Variables

- `DEEPL_API_KEY` - API key for DeepL translation service
- `DISCORD_TOKEN` - token for your Discord bot
- `AUTO_TRANSLATE_CHANNELS` - comma-separated Discord channel IDs where messages will be translated automatically

Do not commit real bot tokens or API keys.

## Status

Learning/pet project. Useful next steps would be Docker packaging, configuration cleanup, tests for translation fallback behavior, and replacing local LibreTranslate URLs with configurable environment variables.
