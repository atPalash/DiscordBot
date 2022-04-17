import asyncio
import threading
import function
import platform
import discord
from discord_messenger import DiscordMessenger

class DiscordListener:
    """
    Create only one Discord Listener
    """
    _token = ""
    _channel_name = ""
    _channel = None
    _client = None
    _loop = None
    _thread = None
    _ready = False
    _route_methods = {}

    @staticmethod
    def initialise(channel_name: str, token: str):
        try:
            if DiscordListener._client is None:
                DiscordListener._channel_name = channel_name
                DiscordListener._token = token
                DiscordListener._client = discord.Client()

                @DiscordListener._client.event
                async def on_ready():
                    DiscordListener._ready = True
                    channels = DiscordListener._client.get_all_channels()
                    DiscordListener._channel = [ch for ch in channels if ch.name == channel_name][0]
                    await DiscordListener._channel.send(f"{platform.system()}: Discord listener ready")

                @DiscordListener._client.event
                async def on_message(message):
                    if not DiscordListener._ready:
                        return

                    if message.author == DiscordListener._client.user:
                        return

                    if message.channel.name == DiscordListener._channel_name or "clear" in message.system_content:
                        # await message.channel.send("lets do some query")
                        await DiscordListener.parse_msg(message)

            else:
                raise Exception("Must not create multiple Discord listener")
        except Exception as e:
            raise

    @staticmethod
    def run():
        try:
            if DiscordListener._loop is None:
                DiscordListener._loop = asyncio.get_event_loop()
                DiscordListener._loop.create_task(DiscordListener._client.start(DiscordListener._token))
                DiscordListener._thread = threading.Thread(target=DiscordListener._loop.run_forever).start()
            else:
                raise Exception("should not run multiple event listener loops")
        except Exception as e:
            raise

    @staticmethod
    def stop():
        try:
            DiscordListener._loop.stop()
        except Exception as e:
            raise

    @staticmethod
    def add_route(route: str, method: function):
        DiscordListener._route_methods[route] = method

    @staticmethod
    async def __call_route(route: str, *args):
        try:
            if route == "clear":
                await DiscordListener.clear(*args)
                return
            res = DiscordListener._route_methods[route](*args)
            await DiscordListener._channel.send(f"response:\n {res}")
        except Exception as e:
            await DiscordListener._channel.send(f"This route is not available error {str(e)}")
            raise

    @staticmethod
    async def parse_msg(message):
        """
        Message are in format of <command>:<data>
        """
        try:
            msg = message.system_content.replace(" ", "")
            msg = msg.split(":")

            if len(msg) != 2:
                await DiscordListener._channel.send(f"Error in query, it should be <query>:<data>")
                return
            await DiscordListener.__call_route(msg[0], msg[1], message)
        except Exception as e:
            await DiscordListener._channel.send(f"Check your query format error {str(e)}")
            raise

    @staticmethod
    async def clear(*args):
        try:
            channel = args[1].channel
            limit = int(args[0])
            await channel.purge(limit=limit)
            await channel.send(f"deleted previous {limit} messages")
        except Exception as e:
            raise


if __name__ == "__main__":
    # from pathlib import Path
    # import sys
    # module_path = Path("utility").resolve(strict=True).as_posix()

    # # append this submodule to sys path
    # sys.path.append(module_path)
    # from reader import read_config
    # from pathlib import Path

    # conf_folder = Path("conf")
    # discord_config = conf_folder / "discord.yml"
    # discord_config = discord_config.resolve(strict=True).as_posix()
    # discord_config = read_config(discord_config)

    # DiscordListener.initialise("query", discord_config['listener']['bot']['token'])
    # DiscordListener.run()

    # def hello(data):
    #     res = f"Hello from discord you said {data}"
    #     return res
    #
    # def add(data):
    #     val = data.split(",")
    #     val1 = float(val[0])
    #     val2 = float(val[1])
    #     res = val1 + val2
    #     return str(res)

    # DiscordListener.add_route("hello", hello)
    # DiscordListener.add_route("add", add)
    # DiscordListener.run()
