import discord
from discord.ext import commands
import aiohttp
import logging
import os


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discordbot")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# channels where messages will be automatically translated
AUTO_TRANSLATE_CHANNELS = [
    int(ch) for ch in os.getenv("AUTO_TRANSLATE_CHANNELS", "").split(",") if ch
]

TARGET_LANGS = ["hu", "nl", "uk", "de", "fr", "pl", "en"]
FLAGS = {
    "hu": "🇭🇺",
    "nl": "🇳🇱",
    "uk": "🇺🇦",
    "de": "🇩🇪",
    "fr": "🇫🇷",
    "pl": "🇵🇱",
    "en": "🇺🇸"
}
FLAG_TO_LANG = {v: k for k, v in FLAGS.items()}

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
TRANSLATE_API = "http://192.168.31.125:5000/translate"

async def translate_deepl(text, target_lang):
    url = "https://api-free.deepl.com/v2/translate"
    lang_mapping = {
        "uk": "UK",
        "hu": "HU",
        "nl": "NL",
        "de": "DE",
        "fr": "FR",
        "pl": "PL",
        "en": "EN"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data={
                "auth_key": DEEPL_API_KEY,
                "text": text,
                "target_lang": lang_mapping.get(target_lang, target_lang).upper()
            }) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["translations"][0]["text"]
                else:
                    logger.warning(f"DeepL failed with status {resp.status}")
                    raise Exception("DeepL translation failed")
        except Exception as e:
            logger.error(f"Error in DeepL translation: {e}")
            raise e

async def translate_libretranslate(text, target_lang):
    async with aiohttp.ClientSession() as session:
        async with session.post(TRANSLATE_API, json={
            "q": text,
            "source": "auto",
            "target": target_lang,
            "format": "text"
        }) as resp:
            data = await resp.json()
            return data.get("translatedText", "")

async def smart_translate(text, target_lang):
    try:
        return await translate_deepl(text, target_lang)
    except Exception:
        return await translate_libretranslate(text, target_lang)

@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if AUTO_TRANSLATE_CHANNELS and message.channel.id not in AUTO_TRANSLATE_CHANNELS:
        return

    if message.stickers or "http://" in message.content or "https://" in message.content:
        return

    text = message.content
    author_name = message.author.display_name
    author_avatar = message.author.avatar.url if message.author.avatar else None

    results = {}
    for lang in TARGET_LANGS:
        translated = await smart_translate(text, lang)
        results[lang] = translated

    output_text = ""
    for lang in TARGET_LANGS:
        output_text += f"{FLAGS[lang]} {lang.upper()}: {results[lang]}\n"

    embed = discord.Embed(description=output_text.strip())
    embed.set_author(name=author_name.upper(), icon_url=author_avatar)

    await message.channel.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    emoji = str(reaction.emoji)
    if emoji not in FLAG_TO_LANG:
        return

    lang = FLAG_TO_LANG[emoji]

    if reaction.message.author == bot.user and reaction.message.reference:
        original = await reaction.message.channel.fetch_message(reaction.message.reference.message_id)
        text = original.content
    else:
        text = reaction.message.content

    if reaction.message.stickers or "http://" in text or "https://" in text:
        return

    translated = await smart_translate(text, lang)

    author_name = user.display_name
    author_avatar = user.avatar.url if user.avatar else None

    embed = discord.Embed(description=f"{emoji} {translated}")
    embed.set_author(name=author_name.upper(), icon_url=author_avatar)

    await reaction.message.channel.send(embed=embed)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
