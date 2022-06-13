from discord import ApplicationContext, Bot, Embed, Interaction
import discord
from config import embedColor as color
from helper import ContextHelper as Helper, custom_option


embeds: dict[str, Embed] = {
    "main": Embed(color=color, title="Main Help Page", description="""Owners: `_waifus_empire_#7273` and `Waifu's Empire#7388`

Instagram: [empress_waifu_bot](https://instagram.com/empress_waifu_bot)
Twitter: [empress_waifu](https://twitter.com/empress_waifu)
Reddit: [u/empress_waifu](https://reddit.com/u/empress_waifu)
Facebook: [Empress Waifu](https://www.facebook.com/Empress-Waifu-113027701148159)
Invite: [Invite me](https://discordbotlist.com/bots/empress-waifu)
Vote: [Vote here](https://discordbotlist.com/bots/empress-waifu/upvote)

Birthday: Saturday - 12.02.2022""")
    .set_image(url="https://cdn.discordapp.com/attachments/838912913846304789/896033034787225660/Empress_Waifu.png"),

    "user": Embed(color=color, title="User Help")
    .add_field(name="/user info", value="Provides info about the specified user, if a user is not specified it returns info about the one using the command!", inline=False)
    .add_field(name="/user kick", value="Kick the specified user [Server only] [Staff only]", inline=False)
    .add_field(name="/user ban inside", value="Ban the specified user [Server only] [Staff only]", inline=False)
    .add_field(name="/user ban outside", value="Ban any user by specifying their id, this command should be used with users who are not in the server [Server only] [Staff only]", inline=False)
    .add_field(name="/user timeout add", value="Timeout the specified user, if the user is already on timeout the command will stop [Server only] [Staff only]", inline=False)
    .add_field(name="/user timeout remove", value="Remove the specified user from timeout, if the user is not on timeout the command will stop [Server only] [Staff only]", inline=False)
    .add_field(name="External user commands", value="** **", inline=False)
    .add_field(name="/avatar main", value="Returns yours or the specified user's main avatar", inline=False)
    .add_field(name="/avatar server", value="Returns yours or the specified user's server avatar if possible [Server only]", inline=False),

    "server": Embed(color=color, title="Server Help")
    .add_field(name="/server info", value="Provides info about the server [Server only]", inline=False)
    .add_field(name="/server edit", value="Edit the server's name or icon [Server only] [Staff only]", inline=False)
    .add_field(name="/server create_invite", value="Create an invite to the current channel [Server only]", inline=False)
    .add_field(name="/server template", value="Gives a server template that can be used to create a new server", inline=False),

    "channel": Embed(color=color, title="Channel Help")
    .add_field(name="/channel info", value="Provides info about the specified channel [Server only]", inline=False)
    .add_field(name="/channel create", value="Create a new channel with the given values [Server only] [Staff only]", inline=False)
    .add_field(name="/channel edit", value="Edit the specified voice channel or text channel [Server only] [Staff only]", inline=False)
    .add_field(name="/channel delete", value="Delete the specified voice or text channel [Server only] [Staff only]", inline=False),

    "role": Embed(color=color, title="Role Help")
    .add_field(name="/role info", value="Provides info about the specified role [Server only]", inline=False)
    .add_field(name="/role create", value="Create a new role with the provided values [Server only] [Staff only]", inline=False)
    .add_field(name="/role delete", value="Delete the specified role [Server only] [Staff only]", inline=False)
    .add_field(name="/role add", value="Add a certian role to 3 possible users [Server only] [Staff only]", inline=False),

    "emoji": Embed(color=color, title="Emoji Help")
    .add_field(name="/emoji info", value="Provides info about the specified emoji if possible [Server only]", inline=False)
    .add_field(name="/emoji create", value="Create a new emoji with the provided values [Server only] [Staff only]", inline=False)
    .add_field(name="/emoji edit", value="Edit the name of the specified server emoji [Server only] [Staff only]", inline=False)
    .add_field(name="/emoji delete", value="Delete the specified emoji from the server [Server only] [Staff only]", inline=False),

    "reddit": Embed(color=color, title="Reddit Help")
    .add_field(name="/reddit search", value="Get a post from any subreddit you want as long as it is not private", inline=False)
    .add_field(name="/reddit memes", value="Get a random meme from r/memes - r/animememes - r/hentaimemes", inline=False)
    .add_field(name="/reddit hentai", value="Get a random hentai pic from r/hentai", inline=False)
    .add_field(name="/reddit ecchi", value="Get a random ecchi pic from r/ecchi", inline=False)
    .add_field(name="/reddit hentaibdsm", value="Get a random hentai pic from r/hentaibondage", inline=False)
    .add_field(name="/reddit yuri", value="Get a random yuri pic from r/yuri", inline=False)
    .add_field(name="/reddit yaoi", value="Get a random yaoi pic from r/yaoi", inline=False)
    .add_field(name="/reddit cosplay", value="Get a random cosplay pic from r/cosplaygirls", inline=False)
    .add_field(name="/reddit porn", value="Get a random hot pic from r/adorableporn", inline=False)
    .add_field(name="/reddit genshinhentai", value="Get a random hentai pic from r/GenshinImpactHentai", inline=False)
    .add_field(name="/reddit feet", value="Get a random feet pic from r/AnimeFeets", inline=False)
    .add_field(name="Coming soon", value="**/reddit wallpaper** => r/Animewallpaper - r/NSFWAnimeWallpaper", inline=False),

    "bot": Embed(color=color, title="Bot Help")
    .add_field(name="/bot feedback", value="Send feedback about the bot", inline=False)
    .add_field(name="/bot reportproblem", value="Report any problem that you had while using the bot", inline=False)
    .add_field(name="/bot suggest", value="Suggest a command or a feature", inline=False)
    .add_field(name="/bot vote", value="vote for the bot", inline=False)
    .add_field(name="/External bot commands", value="** **", inline=False)
    .add_field(name="/help", value="Provides help", inline=False),

    "games": Embed(color=color, title="Games Help")
    .add_field(name="/games dice", value="Roll a die", inline=False)
    .add_field(name="/games rps", value="Play rock/paper/scissors with the bot", inline=False)
    .add_field(name="/games magic8ball", value="Ask the bot a question and it will answer", inline=False)
    .add_field(name="/games coinflip", value="Flip a coin and bet on it", inline=False),

    "math": Embed(color=color, title="Math Help")
    .add_field(name="/math add", value="Add two numbers together", inline=False)
    .add_field(name="/math subtract", value="Subtract number2 from number1", inline=False)
    .add_field(name="/math multiply", value="Multiply two numbers", inline=False)
    .add_field(name="/math divide", value="Divide two numbers", inline=False)
    .add_field(name="/math power", value="Raise number1 to the power of number2", inline=False),

    "other": Embed(color=color, title="Free commands")
    .add_field(name="/say", value="Say something in the chat", inline=False)
    .add_field(name="/thread", value="Start a new thread in the current channel or on a different channel [Server only]", inline=False)
    .add_field(name="/announce", value="Announce anything for the entire server [Server only] [Staff only]", inline=False)
    .add_field(name="/clear", value="Delete any amount of messages from 1 to 1000 [Server only] [Staff only]", inline=False)
    .add_field(name="Nsfw commands", value="** **", inline=False)
    .add_field(name="/yandere", value="Get a post from yande.re", inline=False)
    .add_field(name="/danbooru", value="Get a post from danbooru", inline=False)
}


class HelpView(discord.ui.View):

    def __init__(self, embeds: dict[str, Embed]):
        super().__init__(timeout=None)
        self.add_item(self.HelpMenu(embeds))

    class HelpMenu(discord.ui.Select):

        __select_options__: list[discord.SelectOption] = [
            discord.SelectOption(label="main page", value="main"),
            discord.SelectOption(label="channel help", value="channel"),
            discord.SelectOption(label="user help", value="user"),
            discord.SelectOption(label="server help", value="server"),
            discord.SelectOption(label="role help", value="role"),
            discord.SelectOption(label="emoji help", value="emoji"),
            discord.SelectOption(label="reddit help", value="reddit"),
            discord.SelectOption(label="bot help", value="bot"),
            discord.SelectOption(label="games help", value="games"),
            discord.SelectOption(label="math help", value="math"),
            discord.SelectOption(label="other commands", value="other")
        ]

        def __init__(self, embeds: dict[str, Embed]) -> None:
            self.embeds = embeds
            super().__init__(placeholder="Select a command help page", options=self.__select_options__)

        async def callback(self, interaction: Interaction):
            await interaction.response.edit_message(embed=self.embeds.get(self.values[0]))


def _helper(bot: Bot):

    @bot.command(name="help", description="Get help for the available commands")
    async def help(ctx: ApplicationContext):
        helper = Helper.from_context(ctx)
        await helper.respond(embed=embeds["main"], view=HelpView(embeds))


if __name__ != "__main__":
    helper = _helper
