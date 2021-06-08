import discord
from discord.ext import commands

TOKEN = "ODUwNTM1MjMxMzY2MTAzMDgy.YLrIqQ.rXvnOk_ZqlkgkIgGEArb6EOFi30"
GUILD = "849417383042875443"

bot = commands.Bot(
    command_prefix=">",
    activity=discord.Activity(type=discord.ActivityType.listening, name=">help"),
)


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


initial_extensions = ['cogs.error_handling',
                      'cogs.dm_settings',
                      'cogs.list_commands',
                      'cogs.message_listener']

if __name__ == "__main__":
    for extension in initial_extensions:
        bot.load_extension(extension)


bot.run(TOKEN, bot=True, reconnect=True)
