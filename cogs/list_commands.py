import sqlite3

import discord
from discord.ext import commands

connection = sqlite3.connect("dm_bot.db")

cursor = connection.cursor()


class List_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def list_commands(self, ctx):
        """See a list of commands for the user."""
        member = ctx.author

        commands_string = await list_user_commands(ctx)

        embed = discord.Embed(
            title=f"{member.display_name}'s Commands",
            description=f"{commands_string}",
            color=0x000000,
        )

        await ctx.send(embed=embed)


async def list_user_commands(ctx):
    member = ctx.author
    user = member.id

    commands_list = cursor.execute(
        """SELECT command FROM user_commands WHERE discord_user = (?) AND enabled = (?)""",
        (user, 1),
    ).fetchall()

    commands_string = " "

    for item in commands_list:
        commands_string += item[0] + "\n"

    if commands_string == " ":
        commands_string = "You don't have any commands set."

    return commands_string


def setup(bot):
    bot.add_cog(List_Commands(bot))
    