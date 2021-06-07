import sqlite3
import datetime


import discord
from discord import channel
from discord.ext import commands

TOKEN = "TOKEN"
GUILD = "GUILD"

bot = commands.Bot(
    command_prefix=">",
    activity=discord.Activity(type=discord.ActivityType.listening, name=">help"),
)


connection = sqlite3.connect("C:\\Users\\alexp\\Dm Bot\\dm_bot.db")

cursor = connection.cursor()


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f"{bot.user} is connected to the following guild:\n"
        f"name: {guild.name}, id: {guild.id}"
    )


bot.remove_command("help")


class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(description=page)
            await destination.send(embed=embed)


bot.help_command = Help(command_attrs={"hidden": True})


class DM_settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dm_add(self, ctx, *, command):
        """Add command to monitor"""
        user = ctx.author
        user = user.id

        find_command = cursor.execute(
            f"""SELECT command, enabled FROM user_commands WHERE command = (?) AND discord_user = (?)""",
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
    bot.add_cog(DM_settings(bot))


setup(bot)


@bot.listen("on_message")
async def message_listener(message):
    if message.author.bot is False:
        bot_message = await wait_for_func(message)

        command, is_command = await is_user_command(message)

        if is_command is True:
            if bot_message.embeds:
                if not len([e for e in bot_message.embeds if e.type == "rich"]) == 0:
                    embed = await dm_if_embed(message, command)
                    return await message.author.send(embed=embed)

                embed = await dm_if_link(message, command, bot_message)
                return await message.author.send(embed=embed)

            embed = await dm_if_not_embed(message, command, bot_message)
            return await message.author.send(embed=embed)


async def wait_for_func(message):
    channel = message.channel

    def check(m):
        return m.author.bot and m.channel == channel

    msg = await bot.wait_for("message", check=check)

    return msg


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
    value = f"[{bot_message.content[0:80]}]({bot_message.content})"

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
        color=0x0000,
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


bot.run(TOKEN)
