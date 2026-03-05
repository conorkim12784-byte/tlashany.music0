import sys

from pyrogram import Client
from pyrogram.types import BotCommand

import config

from ..logging import LOGGER


class YukkiBot(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot")
        super().__init__(
            "YukkiMusicBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        if get_me.last_name:
            self.name = get_me.first_name + " " + get_me.last_name
        else:
            self.name = get_me.first_name
        try:
            await self.send_message(config.LOG_GROUP_ID, "✅ Bot Started")
        except Exception as e:
            LOGGER(__name__).warning(f"Could not send to log group: {e}")
        if config.SET_CMDS == str(True):
            try:
                await self.set_bot_commands([
                    BotCommand("ping", "Check that bot is alive or dead"),
                    BotCommand("play", "Starts playing the requested song"),
                    BotCommand("skip", "Moves to the next track in queue"),
                    BotCommand("pause", "Pause the current playing song"),
                    BotCommand("resume", "Resume the paused song"),
                    BotCommand("end", "Clear the queue and leave voice chat"),
                    BotCommand("shuffle", "Randomly shuffles the queued playlist."),
                    BotCommand("playmode", "Allows you to change the default playmode for your chat"),
                    BotCommand("settings", "Open the settings of the music bot for your chat.")
                ])
            except:
                pass
        LOGGER(__name__).info(f"MusicBot Started as {self.name}")
