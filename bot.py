import os
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

PRODUCTION: bool = bool(int(os.getenv('PRODUCTION')))
PREFIX: str = str(os.getenv('PREFIX'))

intents = discord.Intents.default()
intents.bans = False
intents.voice_states = False

bot = commands.Bot(command_prefix=f'{PREFIX} ', case_insensitive=True,
                   intents=intents, help_command=None,
                   guild_ready_timeout=1, max_messages=None,
                   description='Seamless GitHub-Discord integration.',
                   fetch_offline_members=False)

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s: %(message)s')
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logger = logging.getLogger('main')

extensions: list = [
    'core.background',
    'cogs.github.base.user',
    'cogs.github.base.org',
    'cogs.github.base.repo',
    'cogs.github.numbered.pr',
    'cogs.github.numbered.issue',
    'cogs.github.other.lines',
    'cogs.github.other.info',
    'cogs.help',
    'cogs.config',
    'cogs.debug',
    'cogs.bot_info',
    'cogs.handle.errors',
    'cogs.handle.events'
]

if PRODUCTION:
    extensions.extend([f'cogs.botlists.{file[:-3]}' for file in os.listdir('cogs/botlists')])

for extension in extensions:
    logger.info(f'Loading {extension}...')
    bot.load_extension(extension)


@bot.check
async def global_check(ctx: commands.Context) -> bool:
    if not isinstance(ctx.channel, discord.DMChannel) and ctx.guild.unavailable:
        return False

    return True


async def before_invoke(ctx: commands.Context) -> None:
    await ctx.channel.trigger_typing()


bot.before_invoke(before_invoke)


@bot.event
async def on_ready() -> None:
    logger.info(f'The bot is ready.')
    logger.info(f'discord.py version: {discord.__version__}\n')


if __name__ == '__main__':
    bot.run(os.getenv('BOT_TOKEN'))