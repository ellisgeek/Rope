"""Rope
A Discord <-> Hangouts Bridge.
"""

import asyncio
import discord.discord as discord
import hangups
import logging
import config
import signal
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logFormatter)

#fileHandler = logging.FileHandler("Rope.log")
#fileHandler.setLevel(logging.DEBUG)
#fileHandler.setFormatter(logFormatter)

logger.addHandler(consoleHandler)
#logger.addHandler(fileHandler)

#initialize discord client
discordClient = discord.Client()


# Obtain hangups authentication cookies, prompting for username and
# password from standard in if necessary.
cookies = hangups.auth.get_auth_stdin(config.HANGUPS_TOKEN)

# Instantiate hangups Client instance.
hangupsClient = hangups.Client(cookies)

def signal_handler(sig, frame):
    logger.info('Caught signal', sig)
    if sig == signal.SIGTERM or sig == signal.SIGINT:
        logger.info("Exiting")
        discordClient.close()
        hangupsClient.close()
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

hangouts = discord.Game(name='Hangouts', url="https://hangouts.google.com", type=1)

@discordClient.event
async def on_ready():
    logger.info('Logged in as {0}({1})'.format(discordClient.user.name, discordClient.user.id))
    logger.info("READY")
    await discordClient.change_status(game=hangouts)

@discordClient.event
async def on_message(message):
    logger.debug("Received message from {0} in {1}: {2}".format(message.author.display_name, message.channel, message.content))

    # we do not want the bot to reply to itself
    if message.author == discordClient.user or not message.channel.name == "testing":
        return
    elif message.content.startswith("!@#exit"):
        logging.info("Got magic exit sequence, Exiting!")
        await discordClient.delete_message(message)
        await discordClient.close()

    else:
        await discordClient.change_nickname(discord.utils.get(message.server.members, name=discordClient.user.name), "[Hangouts: {0}] {1}".format("CHAT NAME", message.author.display_name))
        await discordClient.send_message(message.channel, "Received message from {0}: {1}".format(message.author.display_name, message.content))
        await discordClient.change_nickname(discord.utils.get(message.server.members, name=discordClient.user.name), config.DISCORD_NICK)

discordClient.run(config.DISCORD_TOKEN)