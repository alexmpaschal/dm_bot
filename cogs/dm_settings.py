import sqlite3

from discord.ext import commands

connection = sqlite3.connect("dm_bot.db")

cursor = connection.cursor()


class DM_Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dm_add(self, ctx, *, command):
        """Add command to monitor"""
        user = ctx.author
        user = user.id

        find_command = cursor.execute(
            """SELECT command, enabled FROM user_commands WHERE command = (?) AND discord_user = (?)""",
            (command, user),
        ).fetchone()

        if find_command is not None:
            # check enabled value
            if find_command[1] == 1:
                return await ctx.send("You already have that command enabled.")

            return await toggle_on(ctx, user, command)

        return await add_command(ctx, user, command)

    @commands.command()
    async def dm_remove(self, ctx, *, command):
        """Remove monitored command"""
        user = ctx.author
        user = user.id

        find_command = cursor.execute(
            f"""SELECT command, enabled FROM user_commands WHERE command = (?) AND discord_user = (?)""",
            (command, user),
        ).fetchone()

        if find_command is not None:
            if find_command[1] == 0:
                return await ctx.send("You already have that command toggled off.")

            return await toggle_off(ctx, user, command)

        return await ctx.send("That command is not toggled on.")


async def add_command(ctx, user, command):
    cursor.execute(
        f"""INSERT INTO user_commands (discord_user, command, enabled) VALUES (?, ?, ?)""",
        (user, command, 1),
    )
    connection.commit()

    return await ctx.send(f"You will now be notified everytime you use `{command}`.")


async def toggle_on(ctx, user, command):
    cursor.execute(
        """ UPDATE user_commands SET enabled = (?) WHERE discord_user = (?) AND command = (?)""",
        (1, user, command),
    )
    connection.commit()

    return await ctx.send(f"Notifications for `{command}` toggled on.")


async def toggle_off(ctx, user, command):
    cursor.execute(
        """ UPDATE user_commands SET enabled = (?) WHERE discord_user = (?) AND command = (?)""",
        (0, user, command),
    )
    connection.commit()

    return await ctx.send(f"Notifications for `{command}` toggled off.")


def setup(bot):
    bot.add_cog(DM_Settings(bot))
    