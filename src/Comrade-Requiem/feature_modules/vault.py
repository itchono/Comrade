from dis_snek.models.snek import (Scale, InteractionContext,
                                  context_menu, CommandTypes)
from dis_snek.models.discord import (ActionRow, Message,
                                     Button, ButtonStyles)

from logger import log
import asyncio


class Vault(Scale):
    # Allows users to vote to vault a post.
    @context_menu(name="Vault Post",
                  context_type=CommandTypes.MESSAGE,
                  scopes=[419214713252216848])
    async def vault_vote(self, ctx: InteractionContext):
        '''
        Spawns a button to vote for the post.
        '''

        # Get the message to be voted on.
        vault_message: Message = await ctx.channel.get_message(ctx.target_id)

        special_id = f"vault{ctx.target_id}"

        button = Button(ButtonStyles.PRIMARY,
                        emoji="🍅",
                        label="Vault This Post!",
                        custom_id=special_id)

        components: list[ActionRow] = [
            ActionRow(button)
            ]
        sent_message = await ctx.send(
            components=components,
            content="Another user must press the button"
            "to vault the post! You have 180 seconds to vote." + " " +
            vault_message.jump_url)

        def check(button: Button):
            return button.context.author != ctx.author

        try:
            used_component = await self.bot.wait_for_component(
                components=components, check=check, timeout=180)

        except asyncio.TimeoutError:
            await sent_message.edit(components=[])

        else:
            await used_component.context.send(
                f"<Post would be vaulted>, vote cast by {used_component.context.author}")
            await sent_message.edit(components=[])


def setup(bot):
    Vault(bot)
    log.info("Module vault.py loaded.")
