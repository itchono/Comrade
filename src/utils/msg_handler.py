from utils.utilities import *


from fuzzywuzzy import fuzz

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot:

            if jokeMode(await self.bot.get_context(message)):

                # TODO turn this into triggerable behaviour {partial match, full match}
                if "hello comrade" in message.content.lower():
                    await delSend(await self.bot.get_context(message), "Henlo")

                if message.content.lower() == "wait":
                    await delSend(await self.bot.get_context(message), "https://www.youtube.com/watch?v=sBl9qcaQos4")
                
                if "cesb" in message.content.lower():
                    await delSend(await self.bot.get_context(message), "https://www.youtube.com/watch?v=ON-7v4qnHP8")

                if "mtc" in message.content.lower():
                    await delSend(await self.bot.get_context(message), "https://www.youtube.com/watch?v=bO-NaEj2dQ0")
                
                if "approved" in message.content.lower():
                    with open("vid/meme_approved.mp4", "rb") as f: await message.channel.send(file=discord.File(f, "meme_approved.mp4"))
                    
                if message.content.lower() == "i dunno":
                    with open("vid/meme_what.mp4", "rb") as f: await message.channel.send(file=discord.File(f, "i_dunno.mp4"))

                

                if fuzz.token_set_ratio(message.content, "still at cb") > 90:
                    await message.channel.send("And that's okay!")

                if "@someone" in message.content.lower():
                    e = discord.Embed(description=random.choice(list(message.guild.members)).mention)
                    e.set_footer(text=f"Random ping by: {message.author.display_name}")
                    await message.channel.send(embed=e)

                    '''c = self.bot.get_cog("Echo")
                    await c.echo(await self.bot.get_context(message), random.choice(list(message.guild.members)).mention, str(message.author.id), deleteMsg=False)
                    '''
                Knuckles_VD = [
                "meme_approved.mp4", "meme_what.mp4", "meme_denied.mp4",
                "meme_huh.mp4", "meme_illegal.mov",
                "no_meme_no_meme_no_meme.mp4", "meme_no.mp4",
                "meme_already_approved.mp4", "meme_wait.mp4",
                "meme_purple.mp4", "meme_eggman_steal.mp4", "Meme_failed.mp4",
                "meme.mp4", "meme_rick_roll.mov", "Memes.mov", "Giorno.mp4", "meme_doom.mp4"
                ]

                if message.guild and message.channel.id == DBcfgitem(message.guild.id,"meme-channel"):

                    fn = "meme_what.mp4"  # default safety

                    if len(message.attachments) > 0:
                        attach = message.attachments[0].filename
                        fn = Knuckles_VD[hash(attach) % len(Knuckles_VD)]
                        with open("vid/{}".format(fn), "rb") as f:
                            await message.channel.send(file=discord.File(f, fn))

                    elif len(message.embeds) > 0:
                        attach = message.embeds[0].url
                        fn = Knuckles_VD[hash(attach) % len(Knuckles_VD)]
                        with open("vid/{}".format(fn), "rb") as f:
                            await message.channel.send(file=discord.File(f, fn))

                    elif match_url(message.content.lower()):
                        # just a plain link
                        attach = message.content.lower()
                        fn = Knuckles_VD[hash(attach) % len(Knuckles_VD)]
                        with open("vid/{}".format(fn), "rb") as f:
                            await message.channel.send(file=discord.File(f, fn))
                            
            if not isNotThreat(1)(await self.bot.get_context(message)) and (len(
                    message.attachments) + len(
                    message.embeds) > 0 or match_url(message.content)):
                e = discord.Embed(title="You just posted cringe")
                e.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/419214713755402262/709165272447057981/unknown-11.png"
                )
                await message.channel.send(embed=e)

            