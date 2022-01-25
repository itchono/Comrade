'''
Powerful core feature of Comrade which
allows messsages to be sent under the guise of another person
'''

from dis_snek.models.discord import GuildText, Message, Webhook, Member
from dis_snek.models.snek import Context


async def mimic(channel: GuildText, content:str=None,
                username: str=None, avatar_url: str=None, **kwargs):
    '''
    Sends a mimic message in a channel using a webhook,
    allowing the bot to use a different name, and avatar
    '''
    # Set up webhook if it doesn't already exist
    # if there are no webhook permissions, send it directly using the bot
    try:
        # Try to find webhook named "Comrade"
        channel_webhooks = await channel.get_webhooks()
        webhook: Webhook = next(filter(lambda w: w.name == "Comrade", channel_webhooks), None)

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


async def echo(ctx: Context, member: Member,
               content=None, **kwargs):
    '''
    Sends a mimic as a specific person -- entry point from slash command
    '''
    await mimic(ctx.channel, content=content,
                username=member.display_name,
                avatar_url=member.avatar.url, **kwargs)
    if not ctx.responded:
        await ctx.send("Echoed!", ephemeral=True)


def isWebhook(message: Message) -> bool:
    # Checks if it's a webhook
    return message.author.discriminator == "0000"
