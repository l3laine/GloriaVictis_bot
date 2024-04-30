import datetime
import os
import discord
import logging
import command_operations

from src.GloriaVictis_bot.discordReadWrite import get_config_from_json, get_config_parameter, get_supported_commands, \
    check_json_integrity, get_discord_token
from src.GloriaVictis_bot.logging_utilities import prepare_logger

logger = logging.getLogger("gv")

config = get_config_from_json()

page = config["page"]

command_ops = command_operations.CommOp()

client = command_ops.get_client()


async def schedule_daily_message():
    current = datetime.datetime.now()
    # last_message = date
    # if current - last_message == 1 day


@client.event
async def on_ready():
    print(f"Discord library version: {discord.__version__}")
    (json_integrity_print, json_integrity_result) = check_json_integrity()
    if not json_integrity_result:
        raise RuntimeError(json_integrity_print)
    print(json_integrity_print)
    prepare_logger()
    logger.info(json_integrity_result)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.author.guild_permissions.administrator and message.content.startswith("!gvsetchannel "):
        await command_ops.gv_set_channel(message)
        return
    if message.author.guild_permissions.administrator and message.content == "!gvgo":
        await command_ops.gv_go()
        return
    if message.author.guild_permissions.administrator and message.content == "!gvr":
        await command_ops.gv_remove_old()
        return
    if message.author.guild_permissions.administrator and message.content.startswith("!gv"):
        supported_commands = get_supported_commands()
        await message.channel.send(supported_commands)


client.run(get_discord_token())
