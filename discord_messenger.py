import discord


class DiscordMessenger:
    """
    Add webhook to discord to send message on channel
    """
    _webhook_urls = {}
    _webhooks = {}

    @staticmethod
    def initialise(general_webhook_url: str):
        """
        A general channel is created by default to report issues in discord. User should pass webhook url of atleast
        one channel named general to initialise.
        """
        try:
            if DiscordMessenger._webhooks.get("general") is None:
                DiscordMessenger.add_webhook(webhook_name="general", webhook_url=general_webhook_url)
        except Exception as e:
            raise

    @staticmethod
    def add_webhook(webhook_name: str, webhook_url: str):
        """
        Add webhook and start sending messages
        """
        try:
            DiscordMessenger._webhook_urls[webhook_name] = webhook_url
            DiscordMessenger._webhooks[webhook_name] = discord.Webhook.from_url(webhook_url,
                                                                                adapter=discord.RequestsWebhookAdapter())
        except Exception as e:
            raise

    @staticmethod
    def send_message(channel: str, msg: str):
        try:
            DiscordMessenger._webhooks[channel].send(msg)
        except Exception as e:
            raise
