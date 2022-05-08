import discord


class DiscordMessengerConfig:
    def __init__(self, webhook_urls=None, webhooks=None):
        self.webhook_urls = webhook_urls
        self.webhooks = webhooks
        self.EMBEDDED_MSG_SIZE = 2096


class DiscordMessenger:
    """
    Add webhook to discord to send message on channel
    """
    _discord_messenger_config = None

    @staticmethod
    def initialise(webhook_urls: dict = None):
        """
        A general channel is created by default to report issues in discord. User should pass webhook url of atleast
        one channel named general to initialise.
        """
        try:
            if DiscordMessenger._discord_messenger_config is None:
                DiscordMessenger._discord_messenger_config = DiscordMessengerConfig()
                DiscordMessenger.add_webhook(webhook_urls)

            return DiscordMessenger._discord_messenger_config

        except Exception as e:
            raise

    @staticmethod
    def add_webhook(webhook_urls: dict):
        """
        Add webhook and start sending messages
        """
        if webhook_urls is not None and DiscordMessenger._discord_messenger_config is not None:
            try:
                webhooks = {}
                for k, v in webhook_urls.items():
                    webhooks[k] = discord.Webhook.from_url(v, adapter=discord.RequestsWebhookAdapter())

                DiscordMessenger._discord_messenger_config.webhook_urls = webhook_urls
                DiscordMessenger._discord_messenger_config.webhooks = webhooks
            except Exception as e:
                raise
        else:
            raise Exception("Should pass dictionary of urls / initiate the messenger")

    @staticmethod
    def send_message(channel: str, msg: str, title: str):
        """
        This singleton class should be initialised first.
        Send message string in bulk.
        """
        messenger = DiscordMessenger._discord_messenger_config
        if messenger is not None:
            try:
                for embed in DiscordMessenger.__convert_to_chunks(title=title, msg=msg,
                                                                  chunk_size=messenger.EMBEDDED_MSG_SIZE):
                    messenger.webhooks[channel].send(embed=embed)
            except Exception as e:
                raise
        else:
            raise Exception("Discord messenger None error")

    @staticmethod
    def __convert_to_chunks(title: str, msg: str, chunk_size=2096):
        """
        Converts the message sent in chunks for proper discord message send.
        """
        embeds = []

        if len(msg) < chunk_size:
            embed = DiscordMessenger.__create_embed(title=title, msg=msg)
            embeds.append(embed)
        else:
            msgs = msg.split('\n')

            des = ""
            for message in msgs:
                message_to_add = message + '\n'
                if len(des + message_to_add) <= chunk_size:
                    des += message_to_add
                else:
                    embed = DiscordMessenger.__create_embed(title=title, msg=des)
                    embeds.append(embed)
                    des = message_to_add

            if len(des) > 3:  # ensure there is message
                embed = DiscordMessenger.__create_embed(title=title, msg=des)
                embeds.append(embed)

        return embeds

    @staticmethod
    def __create_embed(title: str, msg: str):
        embed = discord.Embed()
        embed.title = title
        embed.description = msg
        return embed
