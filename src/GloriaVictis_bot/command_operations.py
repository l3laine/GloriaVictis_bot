import asyncio
import discord
import logging
from discord.ext import commands

from src.GloriaVictis_bot.discordReadWrite import get_config_parameter, set_channels
from src.GloriaVictis_bot.gloriaParser import run

logger = logging.getLogger("gv")


class CommOp:
    intents = discord.Intents(members=True, guilds=True, message_content=True, messages=True)
    client = discord.Client(intents=intents)
    bot = commands.Bot(intents=intents, command_prefix="?")

    def get_client(self):
        return self.client

    async def gv_go(self):
        logger.debug("####### gvGo called #######")
        channel = self.get_client().get_channel(get_config_parameter("channel_id"))
        logging.debug(f"Channel id found:{channel.id}")
        if not self.get_client().get_channel(get_config_parameter("channel_id")):
            logging.info("The channel " + get_config_parameter("channel_id") + " doesn't exist!")
        loop = asyncio.get_event_loop()
        generated_message = await loop.run_in_executor(None, run)
        logger.debug("Awaiting the message to be sent.")
        await channel.send(generated_message)
        return

    def is_me(self, m):
        return m.author == self.get_client().user

    async def gv_remove_old(self):
        logger.info("Removing old discord bot messages.")
        channel = self.get_client().get_channel(get_config_parameter("channel_id"))
        guild = channel.guild
        for chan in guild.channels:
            if isinstance(chan, discord.TextChannel):
                await chan.purge(limit=100, check=self.is_me)

    async def gv_set_channel(self, message):
        logger.debug("####### gvSetChannel called #######")
        try:
            id_int = int(message.content[14:])
        except ValueError:
            logger.info("Requested channel ID is not an integer")
            return
        if not self.get_client().get_channel(id_int):
            logger.info("The channel " + str(id_int) + " doesn't exist!")
            return
        set_channels(id_int)
        if isinstance(self.get_client().get_channel(id_int).name, str):
            await message.add_reaction(":thumbs_up:")
            await message.channel.send(
                "I've set the channel I will send tournament info to #" + self.get_client().get_channel(id_int).name)
        return
