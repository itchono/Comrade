'''
Powerful core feature of Comrade which
allows messsages to be sent under the guise of another person
'''

import discord
from discord.ext import commands


async def mimic(channel: discord.TextChannel, content=None,
                username=None, avatar_url: str = None, **kwargs):
    '''
    Sends a mimic message in a channel using a webhook,
    allowing the bot to use a different name, and avatar
    '''
    # Set up webhook if it doesn't already exist
    # if there are no webhook permissions, send it directly using the bot
    try:
        if not (webhook := discord.utils.get(await channel.webhooks(),
                                             name="Comrade")):
            webhook = await channel.create_webhook(name="Comrade",
                                                   avatar=None,
                                                   reason="Comrade "
                                                   "Mimic System")
    except BaseException:
        await channel.send(content=content,
                           username=username,
                           avatar_url=avatar_url,
                           **kwargs)
        return

    await webhook.send(content=content,
                       username=username,
                       avatar_url=avatar_url, **kwargs)


async def echo(ctx: commands.Context, member=discord.Member,
               content=None, delete_msg=False, **kwargs):
    '''
    Sends a mimic as a specific person
    '''
    await mimic(ctx.channel, content=content,
                username=member.display_name,
                avatar_url=member.avatar_url, **kwargs)
    if delete_msg:
        await ctx.message.delete()  # deletes the source message


def isWebhook(message: discord.Message) -> bool:
    # Checks if it's a webhook
    return message.author.discriminator == "0000"
