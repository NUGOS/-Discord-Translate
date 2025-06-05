import types
import sys
import pytest

# stub discord module
discord_stub = types.ModuleType("discord")
class Intents:
    @classmethod
    def default(cls):
        return cls()
    def __init__(self):
        self.message_content = False
        self.reactions = False

discord_stub.Intents = Intents
class Embed:
    def __init__(self, description=None):
        self.description = description
    def set_author(self, name=None, icon_url=None):
        pass

discord_stub.Embed = Embed

discord_ext = types.ModuleType("discord.ext")
commands_stub = types.ModuleType("discord.ext.commands")
class Bot:
    def __init__(self, *args, **kwargs):
        pass
    def event(self, func):
        return func
    def run(self, *args, **kwargs):
        pass

commands_stub.Bot = Bot
discord_ext.commands = commands_stub

sys.modules['discord'] = discord_stub
sys.modules['discord.ext'] = discord_ext
sys.modules['discord.ext.commands'] = commands_stub

# stub aiohttp
aiohttp_stub = types.ModuleType("aiohttp")
class ClientSession:
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, *args, **kwargs):
        class Resp:
            status = 200
            async def json(self):
                return {}
        return Resp()

aiohttp_stub.ClientSession = ClientSession
sys.modules['aiohttp'] = aiohttp_stub

import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "bot", os.path.join(os.path.dirname(__file__), os.pardir, "bot.py")
)
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)
sys.modules['bot'] = bot
smart_translate = bot.smart_translate

@pytest.mark.asyncio
async def test_smart_translate_prefers_deepl(monkeypatch):
    async def fake_deepl(text, lang):
        return 'deepl'
    async def fake_libre(text, lang):
        return 'libre'
    monkeypatch.setattr('bot.translate_deepl', fake_deepl)
    monkeypatch.setattr('bot.translate_libretranslate', fake_libre)
    result = await smart_translate('hi', 'en')
    assert result == 'deepl'

@pytest.mark.asyncio
async def test_smart_translate_fallback(monkeypatch):
    async def fake_deepl(text, lang):
        raise Exception('fail')
    async def fake_libre(text, lang):
        return 'libre'
    monkeypatch.setattr('bot.translate_deepl', fake_deepl)
    monkeypatch.setattr('bot.translate_libretranslate', fake_libre)
    result = await smart_translate('hi', 'en')
    assert result == 'libre'
