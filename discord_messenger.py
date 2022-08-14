import discord

from utility.singleton import Singleton


class DiscordMessengerConfig:
    def __init__(self, webhook_urls=None, webhooks=None):
        self.webhook_urls = webhook_urls
        self.webhooks = webhooks
        self.EMBEDDED_MSG_SIZE = 2096


class DiscordMessenger(metaclass=Singleton):
    """
    Add webhook to discord to send message on channel
    """
    
    def __init__(self, webhook_urls: dict = None):
        self.discord_messenger_config = None
        """
        A general channel is created by default to report issues in discord. User should pass webhook url of atleast
        one channel named general to initialise.
        """
        try:
            if self.discord_messenger_config is None:
                self.discord_messenger_config = DiscordMessengerConfig()
                self.add_webhook(webhook_urls)

        except Exception as e:
            raise

    def add_webhook(self, webhook_urls: dict):
        """
        Add webhook and start sending messages
        """
        if webhook_urls is not None and self.discord_messenger_config is not None:
            try:
                webhooks = {}
                for k, v in webhook_urls.items():
                    webhooks[k] = discord.Webhook.from_url(v, adapter=discord.RequestsWebhookAdapter())

                self.discord_messenger_config.webhook_urls = webhook_urls
                self.discord_messenger_config.webhooks = webhooks
            except Exception as e:
                raise
        else:
            raise Exception("Should pass dictionary of urls / initiate the messenger")

    def send_message(self, channel: str, msg: str, title: str):
        """
        This singleton class should be initialised first.
        Send message string in bulk.
        """
        messenger = self.discord_messenger_config
        if messenger is not None:
            try:
                for embed in self.__convert_to_chunks(title=title, msg=msg, chunk_size=messenger.EMBEDDED_MSG_SIZE):
                    messenger.webhooks[channel].send(embed=embed)
            except Exception as e:
                raise
        else:
            raise Exception("Discord messenger None error")

    def __convert_to_chunks(self, title: str, msg: str, chunk_size=2096):
        """
        Converts the message sent in chunks for proper discord message send.
        """
        embeds = []

        if len(msg) < chunk_size:
            embed = self.__create_embed(title=title, msg=msg)
            embeds.append(embed)
        else:
            msgs = msg.split('\n')

            des = ""
            for message in msgs:
                message_to_add = message + '\n'
                if len(des + message_to_add) <= chunk_size:
                    des += message_to_add
                else:
                    embed = self.__create_embed(title=title, msg=des)
                    embeds.append(embed)
                    des = message_to_add

            if len(des) > 3:  # ensure there is message
                embed = self.__create_embed(title=title, msg=des)
                embeds.append(embed)

        return embeds

    @staticmethod
    def __create_embed(title: str, msg: str):
        embed = discord.Embed()
        embed.title = title
        embed.description = msg
        return embed
