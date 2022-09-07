import asyncio
import json
import threading
import function
import platform
import discord
from discord_messenger import DiscordMessenger
from request import Request
from singleton import Singleton


class DiscordListener(metaclass=Singleton):
    """
    Create only one Discord Listener
    """

    def __init__(self, discord_config: dict, discord_messenger=None):
        self.token = ""
        self.channel_name = ""
        self.channel = None
        self.client = None
        self.loop = None
        self.thread = None
        self.ready = False
        self.route_methods = {}
        self.discord_messenger = discord_messenger
        try:
            self.channel_name = list(discord_config['listener']['webhook'].items())[0][0]
            self.token = list(discord_config['listener']['bot'].items())[0][1]
            self.client = discord.Client()

            # Listener runs in separate thread need to initialise Discord messenger with listener config
            self.discord_messenger = DiscordMessenger(discord_config['messenger']['webhook'])

            @self.client.event
            async def on_ready():
                self.ready = True
                channels = self.client.get_all_channels()
                self.channel = [ch for ch in channels if ch.name == self.channel_name][0]
                self.discord_messenger.send_message(channel=self.channel_name,
                                                    msg=f"{platform.system()}: Discord listener ready",
                                                    title="Listener info")

            @self.client.event
            async def on_message(message):
                if not self.ready:
                    return

                if message.author == self.client.user or message.system_content == "":
                    return

                if message.channel.name == self.channel_name or "clear" in message.system_content:
                    # await message.channel.send("lets do some query")
                    await self.__parse_msg(message)

            self.__run()
        except Exception as e:
            raise

    def __del__(self):
        self.__stop()
        exit(0)

    def add_route(self, route: str, method: function):
        self.route_methods[route] = method

    async def clear(*args):
        try:
            channel = args[1].channel
            limit = int(args[0])
            await channel.purge(limit=limit)
            await channel.send(f"deleted previous {limit} messages")
        except Exception as e:
            raise

    def __stop(self):
        """
        Call stop to stop the loop properly.
        """
        try:
            self.loop.stop()
        except Exception as e:
            raise

    def __run(self):
        try:
            if self.loop is None:
                self.loop = asyncio.get_event_loop()
                self.loop.create_task(self.client.start(self.token))
                self.thread = threading.Thread(target=self.loop.run_forever).start()
            else:
                self.discord_messenger.send_message(channel=self.channel_name, msg="No need to run another instance "
                                                                                   "of discord listener",
                                                    title="Info")
        except Exception as e:
            raise

    # async def __call_route(self, route: str, *args):
    #     try:
    #         if route == "clear":
    #             await self.clear(*args)
    #             return
    #
    #         res = Request.post("http://127.0.0.1:8000/service", data={data: {'args': args[0]}})
    #         self.discord_messenger.send_message(channel=self.channel_name, msg=res['body'], title=route)
    #     except Exception as e:
    #         self.discord_messenger.send_message(channel=self.channel_name,
    #                                             msg=f"This route is not available error {str(e)}",
    #                                             title=type(e).__name__)
    #         raise

    async def __parse_msg(self, message):
        """
        Message are in format of <command>:<data>
        """
        try:
            msg = message.system_content.lower().strip().split(" ", 1)
            if len(msg) == 1 and msg[0] == 'stop':
                await self.channel.send(f"Stopping discord listener")
                self.__del__()
                return

            res = Request.post("http://127.0.0.1:8000/service",
                               data={
                                   'command': msg[0],
                                   'args': msg[1]
                               })

            # await self.__call_route(msg[0].strip(), msg[1].strip())
            self.discord_messenger.send_message(channel=self.channel_name, msg=res['body'], title=msg[0])
        except Exception as e:
            await self.discord_messenger.send_message(channel=self.channel_name,
                                                      msg=f"Check your query format error {str(e)}",
                                                      title=type(e).__name__)
            raise
