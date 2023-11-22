import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

# Your bot token
TOKEN = os.getenv('DISCORD_TOKEN')

# Role and channel information
target_channel_name = os.getenv('DISCORD_CHANNEL', 'test')
target_role_name = os.getenv('DISCORD_ROLE', 'Member')

# Create an instance of the bot with a command prefix
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'You have logged in as {bot.user.name}')

@bot.event
async def on_raw_reaction_add(payload):
    # Check if the reaction is in the specified channel
    channel = bot.get_channel(payload.channel_id)
    if channel.name == target_channel_name:
        # Check if the user has the specified role
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        target_role = discord.utils.get(guild.roles, name=target_role_name)

        if target_role and target_role in member.roles:
            # Remove the reaction
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, member)

@bot.command(name='clean-reactions', aliases=['cr'])
@commands.has_permissions(administrator=True)
async def clean_reactions(ctx):
    # Check all messages in the target channel and remove reactions from users with the specified role
    channel = discord.utils.get(ctx.guild.channels, name=target_channel_name)
    if channel:
        async for message in channel.history(limit=None):
            for reaction in message.reactions:
                async for user in reaction.users():
                    if target_role_name in [role.name for role in user.roles]:
                        await reaction.remove(user)
        logger.info('Reactions cleaned')


if __name__ == "__main__":
    # Run the bot
    bot.run(TOKEN)
