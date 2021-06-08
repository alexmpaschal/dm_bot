import sqlite3
import asyncio
import datetime

import discord
from discord.ext import commands

connection = sqlite3.connect("dm_bot.db")

cursor = connection.cursor()


class Message_Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_command(self, message):
        if message.author.bot is False:
            next_message = await self.wait_for_func(message)

            command, is_command = await is_user_command(message)

            await asyncio.sleep(0.5)

            if is_command is True and next_message is not None:
                if next_message.embeds:
                    if any([e.type == "rich" for e in next_message.embeds]):
                        embed = await dm_if_embed(message, command)
                        return await message.author.send(embed=embed)

                    embed = await dm_if_link(message, command, next_message)
                    return await message.author.send(embed=embed)

                embed = await dm_if_not_embed(message, command, next_message)
                return await message.author.send(embed=embed)


    async def wait_for_func(self, message):
        channel = message.channel

        def check_for_bot_message(m):
            return m.author.bot and m.channel == channel

        def check_for_user_message(m):
            return not m.author.bot and m.channel == channel

        done, pending = await asyncio.wait(
            [
                self.bot.wait_for("message", check=check_for_bot_message),
                self.bot.wait_for("message", check=check_for_user_message),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        next_message = done.pop().result()

        for future in done:
            future.exception()

        for future in pending:
            future.cancel()

        if next_message.author.bot is True:
            return next_message

        return None


async def is_user_command(message):
    user = message.author
    user = user.id
    message_start = message.content.split(" ")[0]

    user_commands = cursor.execute(
        """SELECT command FROM user_commands WHERE discord_user = (?) AND enabled = (?)""",
        (user, 1),
    ).fetchall()

    for command in user_commands:
        if message_start == command[0]:
            return command, True

    return " ", False


async def dm_if_embed(message, command):
    guild = message.guild
    link = message.jump_url

    value = "The bot sent an embed."
    embed = await create_alert_embed(command, guild, message, value, link)

    return embed


async def dm_if_link(message, command, bot_message):
    guild = message.guild
    link = message.jump_url
    link_name = bot_message.content[0:80] + "..."
    value = f"[{link_name}]({bot_message.content})"

    embed = await create_alert_embed(command, guild, message, value, link)

    return embed


async def dm_if_not_embed(message, command, bot_message):
    guild = message.guild
    link = message.jump_url
    this_message = bot_message.content

    if len(this_message) > 80:
        this_message = this_message[0:80] + "..."

    value = f"{this_message}"

    embed = await create_alert_embed(command, guild, message, value, link)

    return embed


async def create_alert_embed(command, guild, message, value, link):
    embed = discord.Embed(
        title="Command Alert",
        description=f"You just used `{command[0]}` in {guild.name}",
        color=0x000000,
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/yaboiwierdal/dm_bot/main/images/circle-cropped(4).png"
    )
    embed.add_field(name="Message", value=f"{message.content}", inline=False)
    embed.add_field(name="Bot's Reply", value=f"{value}", inline=False)
    embed.add_field(
        name="Conversation", value=f"[Jump to message!]({link})", inline=False
    )
    embed.timestamp = datetime.datetime.utcnow()

    return embed


def setup(bot):
    bot.add_cog(Message_Listener(bot))
