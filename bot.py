import discord
from discord.ext import commands
import aiohttp
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discordbot")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

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

DEEPL_API_KEY = "API-KEY"
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
    except:
        return await translate_libretranslate(text, target_lang)

@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author.bot:
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
    if user.bot or reaction.message.author != bot.user:
        return

    emoji = str(reaction.emoji)
    if emoji in FLAG_TO_LANG:
        lang = FLAG_TO_LANG[emoji]
        ref_message = reaction.message.reference
        if ref_message:
            original = await reaction.message.channel.fetch_message(ref_message.message_id)
            text = original.content
        else:
            text = reaction.message.content

        translated = await smart_translate(text, lang)

        author_name = user.display_name
        author_avatar = user.avatar.url if user.avatar else None

        embed = discord.Embed(description=f"{emoji} {translated}")
        embed.set_author(name=author_name.upper(), icon_url=author_avatar)

        await reaction.message.channel.send(embed=embed)

bot.run("TOKEN")
