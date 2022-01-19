from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import context_menu
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.components import ActionRow, Button, ButtonStyles
from dis_snek.models.discord_objects.message import Message
from dis_snek.models.enums import CommandTypes

class Vault(Scale):
    # Allows users to vote to vault a post.
    @context_menu(name="Vault Post", context_type=CommandTypes.MESSAGE, scopes=[419214713252216848])
    async def vault_vote(self, ctx: InteractionContext):
        '''
        Spawns a button to vote for the post.
        '''

        # Get the message to be voted on.
        vault_message: Message = await ctx.channel.get_message(ctx.target_id)

        jump_url = f"https://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{vault_message.id}"

        special_id = f"vault{ctx.target_id}"

        button = Button(ButtonStyles.PRIMARY,
                emoji="🍅",
                label="Vault This Post!",
                custom_id=special_id)

        components: list[ActionRow] = [
            ActionRow(button)
            ]
        sent_message = await ctx.send(components=components,
            content="Press the button to vault the post! You have 180 seconds to vote." + " " + jump_url)

        try:
            used_component = await self.bot.wait_for_component(components=components, timeout=180)

        except TimeoutError:
            await sent_message.edit(components=[])

        else:
            await used_component.context.send("<Post would be vaulted>")
            await sent_message.edit(components=[])

def setup(bot):
    Vault(bot)
    print("Module vault.py loaded.")
            