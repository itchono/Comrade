'''
Powerful core feature of Comrade which
allows messsages to be sent under the guise of another person
'''

from dis_snek.models.discord_objects.channel import GuildText
from dis_snek.models.discord_objects.message import Message
from dis_snek.models.discord_objects.webhooks import Webhook
from dis_snek.models.discord_objects.user import Member
from dis_snek.models.context import InteractionContext
from dis_snek.utils import find


async def mimic(channel: GuildText, content:str=None,
                username: str=None, avatar_url: str=None, **kwargs):
    '''
    Sends a mimic message in a channel using a webhook,
    allowing the bot to use a different name, and avatar
    '''
    # Set up webhook if it doesn't already exist
    # if there are no webhook permissions, send it directly using the bot
    try:
        webhook: Webhook = find(lambda w: w.name == "Comrade", await channel.get_webhooks())

        if not webhook:
            webhook: Webhook = await channel.create_webhook(name="Comrade")

    except BaseException:
        await channel.send(content=content,
                           username=username,
                           avatar_url=avatar_url,
                           **kwargs)
        return

    await webhook.send(content=content,
                       username=username,
                       avatar_url=avatar_url, **kwargs)


async def echo(ctx: InteractionContext, member: Member,
               content=None, **kwargs):
    '''
    Sends a mimic as a specific person -- entry point from slash command
    '''
    await mimic(ctx.channel, content=content,
                username=member.display_name,
                avatar_url=member.avatar.url, **kwargs)
    await ctx.send("Echoed!", ephemeral=True)


def isWebhook(message: Message) -> bool:
    # Checks if it's a webhook
    return message.author.discriminator == "0000"
