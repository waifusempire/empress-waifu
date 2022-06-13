import datetime
from json import JSONDecodeError
import random
import discord
import requests
import asyncio
from config import *
from helper import ContextHelper as Ctx, CustomOption, create_autocomplete, create_view, custom_option, discord_time_formatter
import reddit_idea as Reddit
from yandere.yandere import Yandere
from yandere.yandere_config import YandereConfig


def danbooru(*tags: str) -> dict:
    r = requests.get(
        f"https://danbooru.donmai.us/posts.json/?tags=rating:explicit+{'+'.join(tags)}&limit=100")
    return random.choice(r.json())


reddit_subreddits = ["adorableporn", "GenshinImpactHentai", "ecchi", "cute", "hentai", "yuri", "yaoi",
                     "cosplay", "memes", "animememes", "hentaimemes", "hentaibondage", "Animewallpaper", "AnimeFeets"]


TIME = datetime.datetime.now
NSFWERROR = discord.Embed(color=embedColor, title="Unable to send content!", description="**Reason**\nChannel not marked nsfw!", timestamp=TIME()).set_footer(
    text="Error", icon_url="https://www.downloadclipart.net/large/exclamation-mark-transparent-png.png")
UNSUPPORTEDDM = discord.Embed(color=embedColor, title="Command not available", description="**Reason**\nCommand is a server only command!", timestamp=TIME()).set_footer(
    text="Error", icon_url="https://www.downloadclipart.net/large/exclamation-mark-transparent-png.png")


intents = discord.Intents.default()
intents.members = True


client = discord.Bot(intents=intents)


async def send_message(channel_id: int):
    b = client.get_channel(channel_id)
    await b.send(f"Running, {discord_time_formatter(time_format='R')}\n```\nCommands:\n    Slash commands: {len(client.application_commands)-10}\n    User commands: 5\n    Message commands: 5```")


@client.event
async def on_ready():
    print("-------------------------------------------------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------------------------------------------------")
    print("----------------------------------------------------- online ------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------------------------------------------------")
    print("-------------------------------------------------------------------------------------------------------------------------------------")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{len(client.guilds)} servers | /help"))
    await send_message(channel_id=942526018797830185)
    print("Errors go here-----------------------------------------------------------------------------------------------------------------------\n-------------------------------------------------------------------------------------------------------------------------------------")


channel_command = client.create_group(
    "channel", "This group has the subcommands to work with channels")


@channel_command.command(name="info", description="Get info about a channel, the voice channel has higher priority")
@custom_option("voice_channel", **CustomOption(discord.VoiceChannel, default=None).to_option_dict())
@custom_option("text_channel", **CustomOption(discord.TextChannel, default=None).to_option_dict())
async def info_channel(ctx: discord.ApplicationContext, voice_channel: discord.VoiceChannel = None, text_channel: discord.TextChannel = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if not voice_channel and not text_channel:
        text_channel = helper.channel
    if not voice_channel:
        embed = discord.Embed(color=embedColor, title="Channel Info", timestamp=TIME(),
                              description=f"""**Name**: {text_channel.name}
**Topic**: {text_channel.topic if text_channel.topic else "Not set"}
**Nsfw**: {"On" if text_channel.nsfw else "Off"}
**Id**: {text_channel.id}
**Slowmode**: {str(text_channel.slowmode_delay)+"s" if text_channel.slowmode_delay > 0 else "Not set"}
**Members**: {len(text_channel.members)}
**Threads**: {f"Active - {len(text_channel.threads)} | Archived - {len(await text_channel.archived_threads().flatten())} | Total - {len(text_channel.threads)+len(await text_channel.archived_threads().flatten())}"}
**Creation Date**: {discord_time_formatter(text_channel.created_at, "F")}""")
        await helper.respond(embed=embed)
    else:

        embed = discord.Embed(color=embedColor, title="Channel Info",
                              description=f"""**Name**: {voice_channel.name}
**Id**: {voice_channel.id}
**User Limit**: {voice_channel.user_limit if voice_channel.user_limit != 0 else "No limit"}
**Creation Date**: {discord_time_formatter(voice_channel.created_at, "F")}""", timestamp=TIME())
        await helper.respond(embed=embed)


autocmp = create_autocomplete([discord.OptionChoice(
    "Text Channel"), discord.OptionChoice("Voice Channel")])


@channel_command.command(name="create", description="Create a channel [staff only]")
@custom_option("channel_type", str, name="type", default="Text Channel", autocomplete=autocmp)
@custom_option("nsfw", **CustomOption(bool, default=False).to_option_dict())
@custom_option("topic", **CustomOption(str, default=None).to_option_dict())
@custom_option("slowmode", **CustomOption(int, default=0).to_option_dict())
@custom_option("name", **CustomOption(str).to_option_dict())
@custom_option("user_limit", **CustomOption(int, default=0, min_value=0, max_value=99).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def create_channel(ctx: discord.ApplicationContext, name: str, channel_type: str, nsfw: bool, topic: str, slowmode: int, user_limit: int, reason: str):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        return await helper.respond(embed=UNSUPPORTEDDM)
    if not helper.guild.me.guild_permissions.manage_channels:
        await helper.respond("I require `manage channels` permission for this command")
    else:
        if not helper.author.guild_permissions.manage_channels:
            await helper.respond("You do not have the right permissions for this command")
        else:
            if channel_type == "Voice Channel":
                channel = await helper.guild.create_voice_channel(name, reason=reason, user_limit=user_limit if user_limit <= 99 else 99)
            elif channel_type == "Text Channel":
                channel = await helper.guild.create_text_channel(name.lower(), reason=reason, topic=topic, nsfw=nsfw, slowmode_delay=slowmode)
            await helper.respond(f"Channel created successfully {channel.mention}")


@channel_command.command(description="Delete a channel by id [staff only]")
@custom_option("channel_id", **CustomOption(int).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def delete(ctx: discord.ApplicationContext, channel_id: int, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        return await helper.respond(embed=UNSUPPORTEDDM)
    if not helper.guild.me.guild_permissions.manage_channels:
        await helper.respond("I require `manage channels` permission for this command")
    else:
        if not helper.author.guild_permissions.manage_channels:
            await helper.respond("You do not have the right permissions for this command")
        else:
            for channel in helper.guild.channels:
                if channel.id == int(channel_id):
                    await channel.delete(reason=reason)
                    found = True
                    break
            else:
                found = False

            if found:
                await helper.respond("Channel was successfully deleted!")
            else:
                await helper.respond("Channel was not found!")


@channel_command.command(name="edit", description="Edit the specified channel [staff only]")
@custom_option("nsfw", **CustomOption(bool, default=False).to_option_dict())
@custom_option("topic", **CustomOption(str, default=None).to_option_dict())
@custom_option("slowmode", **CustomOption(int, default=0).to_option_dict())
@custom_option("new_name", **CustomOption(str, default=None).to_option_dict())
@custom_option("user_limit", **CustomOption(int, default=0, min_value=0, max_value=99).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
@custom_option("voice_channel", **CustomOption(discord.VoiceChannel, default=None).to_option_dict())
@custom_option("text_channel", **CustomOption(discord.TextChannel, default=None).to_option_dict())
async def edit_channel(ctx: discord.ApplicationContext, text_channel: discord.TextChannel = None, voice_channel: discord.VoiceChannel = None, new_name: str = None, nsfw: bool = None, topic: str = None, slowmode: int = None, user_limit: int = None, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.guild.me.guild_permissions.manage_channels:
            await helper.respond("I require `manage channels` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_channels:
                await helper.respond("You do not have the right permissions for this command")
            else:
                if not voice_channel and not text_channel:
                    text_channel = helper.channel
                if voice_channel:
                    await voice_channel.edit(name=new_name if new_name else voice_channel.name, user_limit=user_limit if user_limit else voice_channel.user_limit, reason=reason)
                    await helper.respond(f"{voice_channel.mention} was updated successfully")
                else:
                    await text_channel.edit(reason=reason, name=new_name if new_name else text_channel.name, topic=topic if topic else text_channel.topic, nsfw=nsfw if nsfw else text_channel.nsfw, slowmode_delay=slowmode if slowmode else text_channel.slowmode_delay)
                    await helper.respond(f"{text_channel.mention} was updated successfully")


server_command = client.create_group(
    "server", "This command group has the subcommands for working with the server")


@server_command.command(name="info", description="Info about this server")
async def server_info(ctx: discord.ApplicationContext):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await ctx.respond(embed=UNSUPPORTEDDM)
    else:
        guild = helper.guild
        embed = discord.Embed(
            color=embedColor, title="Server Info", timestamp=TIME(), description=f"""**Name**: {guild.name}
**Owner**: {guild.owner.mention if guild.owner else None}
{"**Description**: {}".format(guild.description) if guild.description else "**Description**: Server description not set"}
**Id**: {guild.id}
**Channels**: {len(guild.channels)}
**Members**: {len(guild.members)}
**Roles**: {len(guild.roles)}
**Creation Date**: {discord_time_formatter(guild.created_at, "F")}""").set_thumbnail(url=guild.icon)
        await helper.respond(embed=embed)


@server_command.command(name="edit", description="Edit the server [staff only]")
@custom_option("new_name", **CustomOption(str, default=None).to_option_dict())
@custom_option("icon", **CustomOption(discord.Attachment, default=None).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def edit_server(ctx: discord.ApplicationContext, new_name: str = None, icon: discord.Attachment = None, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await ctx.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.guild.me.guild_permissions.manage_guild:
            await helper.respond("I require `manage server` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_guild:
                await helper.respond("You do not have the right permissions for this command")
            else:
                await helper.edit_guild(reason=reason, name=new_name if new_name else helper.guild.name, icon=await icon.read() if icon else await helper.guild.icon.read())
                await helper.respond("Server was updated successfully")


@server_command.command(name="create_invite", description="Create an invite in the current channel")
async def create_invite(ctx: discord.ApplicationContext):
    helper = Ctx.from_context(ctx)
    if isinstance(helper.channel, discord.DMChannel) or isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.guild.me.guild_permissions.create_instant_invite:
            await helper.respond("I am unable to create an invite")
            return
        if not helper.user.guild_permissions.manage_channels:
            try:
                b = await helper.channel.create_invite(max_age=3600, temporary=False, unique=True)
                await helper.respond(b)
            except:
                await helper.respond("I am unable to create an invite")
        else:
            try:
                b = await helper.channel.create_invite(temporary=False, unique=True)
                await helper.respond(b)
            except:
                await helper.respond("I am unable to create an invite")


@server_command.command(name="template")
async def new_server(ctx: discord.ApplicationContext):
    button1 = discord.ui.Button(style=discord.enums.ButtonStyle.url,
                                label="Template", url="https://discord.new/cbd7wfwPUbaz")
    view = discord.ui.View(timeout=10)
    view.add_item(item=button1)
    await ctx.respond(embed=discord.Embed(color=0xFFB6F5, description="New server [Template](https://discord.new/cbd7wfwPUbaz)"), view=view, ephemeral=True)


user_command = client.create_group(
    "user", "This command group has the subcommands for working with server members")


@user_command.command(name="info", description="Info about the specified user or yourself")
@custom_option("user", **CustomOption(discord.Member, default=None).to_option_dict())
async def user_info(ctx: discord.ApplicationContext, user: discord.Member = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
        return
    else:
        pass
    user = user if user else helper.author
    embed = discord.Embed(color=embedColor, title="User Info", timestamp=TIME(), description=f"""**Name**: {user.name}
**Display Name**: {user.display_name}
**Nickname**: {user.nick}
**Id**: {user.id}
**Roles**: {len(user.roles)-1}
**Color/Colour**: {user.color}
**Avatar**: [View]({user.display_avatar})
**Type**: {"Bot" if user.bot else "User"}
**Created at**: {discord_time_formatter(user.created_at, "F")}
**Joined at**: {discord_time_formatter(user.joined_at, "F")}""")
    embed.set_thumbnail(url=user.display_avatar)
    await helper.respond(embed=embed)


@user_command.command(name="kick", description="Kick a member from the server [staff only]")
@custom_option("user", **CustomOption(discord.Member).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def kick_user(ctx: discord.ApplicationContext, user: discord.Member, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.kick_members:
            await helper.respond("I require `kick members` permission for this command")
        else:
            if helper.me.top_role.position <= user.top_role.position:
                await helper.respond(embed=discord.Embed(color=embedColor, title="Error", description=f"Unable to kick `{user}`", timestamp=TIME()).add_field(name="Reason", value="We share the same role or the user's top role is higher than mine"))
                return
            if not helper.author.guild_permissions.kick_members:
                await helper.respond("You do not have the right permissions for this command")
            else:
                await user.kick(reason=reason)
                await helper.respond(embed=discord.Embed(title="User was kicked", description=f"`{user}` was kicked successfully", timestamp=TIME()).add_field(name="Reason", value=reason, inline=False))


@user_command.command(name="nick", description="View or change your or someone else's nickname")
@custom_option("user", **CustomOption(discord.Member, default=None).to_option_dict())
@custom_option("new_nick", **CustomOption(str, default=None).to_option_dict())
async def user_nick(ctx: discord.ApplicationContext, new_nick: str = None, user: discord.Member = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not new_nick and not user:
            await helper.respond(f"Your current nickname is `{helper.author.nick}`")
        else:
            user = user if user else helper.author
            if not helper.me.guild_permissions.manage_nicknames:
                await helper.respond("I require `manage nicknames` permission for this command")
            else:
                if helper.me.top_role.position <= user.top_role.position:
                    await helper.respond(embed=discord.Embed(color=embedColor, title="Error", description=f"Unable to change `{user}`'s nickname", timestamp=TIME()).add_field(name="Reason", value="We share the same role or the user's top role is higher than mine"))
                else:
                    if user == helper.author and new_nick and user.guild_permissions.change_nickname:
                        await user.edit(nick=new_nick)
                        await helper.respond(f"Your nickname was successfully changed to {new_nick}")
                    elif user == helper.user and new_nick and not user.guild_permissions.change_nickname:
                        await helper.respond("I am unable to change your nickname")
                    elif user != helper.user and new_nick and user.guild_permissions.manage_nicknames:
                        await user.edit(nick=new_nick)
                        await helper.respond(f"{user}'s nickname was successfully changed to {new_nick}")
                    elif user != helper.user and new_nick and not user.guild_permissions.manage_nicknames:
                        await helper.respond(f"Unable to change `{user}`'s nickname, you do not have the right permissions")


ban_command = user_command.create_subgroup("ban", "ban a user")


@ban_command.command(name="inside", description="Ban a server member [staff only]")
@custom_option("user", **CustomOption(discord.Member).to_option_dict())
@custom_option("delete_messages_days", **CustomOption(int, default=0, min_value=0, max_value=7).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def ban_inside(ctx: discord.ApplicationContext, user: discord.Member, delete_messages_days: int = 0, reason: str = None):
    helper = Ctx(context=ctx)
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.ban_members:
            await helper.respond("I require the `ban members` permission for this command")
        else:
            if not helper.author.guild_permissions.ban_members:
                await helper.respond("You do not have the right permissions for this command")
            else:
                if helper.me.top_role.position <= user.top_role.position:
                    await helper.respond(embed=discord.Embed(color=embedColor, title="Error", description=f"Unable to ban `{user}`", timestamp=TIME()).add_field(name="Reason", value="We share the same role or the user's top role is higher than mine"))
                else:
                    if int(delete_messages_days) > 7:
                        days = 7
                    elif int(delete_messages_days) < 0:
                        days = 0
                    else:
                        days = int(delete_messages_days)
                    await user.ban(delete_message_days=days, reason=reason)
                    await helper.respond(embed=discord.Embed(color=embedColor, title="User was banned", description=f"`{user}` was banned successfully", timestamp=TIME()).add_field(name="Reason", value=reason, inline=False))


@ban_command.command(name="outside", description="Ban a non server member [staff only]")
@custom_option("delete_messages_days", **CustomOption(int, default=0, min_value=0, max_value=7).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
@custom_option("id", **CustomOption(int).to_option_dict())
async def ban_outside(ctx: discord.ApplicationContext, id: int, delete_messages_days: int = 0, reason: str = None):
    helper = Ctx(context=ctx)
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.ban_members:
            await helper.respond("I require the `ban members` permission for this command")
        else:
            if not helper.author.guild_permissions.ban_members:
                await helper.respond("You do not have the right permissions for this command")
            else:
                user = await client.fetch_user(id)
                if int(delete_messages_days) > 7:
                    days = 7
                elif int(delete_messages_days) < 0:
                    days = 0
                else:
                    days = int(delete_messages_days)
                await helper.guild.ban(user=user, delete_message_days=days, reason=reason)
                await helper.respond(embed=discord.Embed(color=embedColor, title="User was banned", description=f"`{user}` was banned successfully", timestamp=TIME()).add_field(name="Reason", value=reason, inline=False))


timeout_command = user_command.create_subgroup("timeout", "Time out a user")


@timeout_command.command(name="add", description="Put the specified user on timeout [staff only]")
@custom_option("user", **CustomOption(discord.Member).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
@custom_option("time", **CustomOption(int, description="How long the user should be on timeout (hours)", default=1).to_option_dict())
async def timeout_add(ctx: discord.ApplicationContext, user: discord.Member, time: int = 1, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.moderate_members:
            await helper.respond("I require `timeout members` permission for this command")
        else:
            if helper.me.top_role.position <= user.top_role.position:
                await helper.respond(embed=discord.Embed(color=embedColor, title="Error", description=f"Unable to kick `{user}`", timestamp=TIME()).add_field(name="Reason", value="We share the same role or the user's top role is higher than mine"))
                return
            if not helper.author.guild_permissions.moderate_members:
                await helper.respond("You do not have the right permissions for this command")
            else:
                if not user.timed_out:
                    await user.timeout(datetime.datetime.now()+datetime.timedelta(hours=int(time)-2), reason=reason)
                    await helper.respond(f"`{user}` was successfully put on timeout for {int(time)} hours")
                else:
                    await helper.respond(f"`{user}` already is on timeout")


@timeout_command.command(name="remove", description="Remove the specified user from timeout [staff only]")
@custom_option("user", **CustomOption(discord.Member).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def timeout_remove(ctx: discord.ApplicationContext, user: discord.Member, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.moderate_members:
            await helper.respond("I require `timeout members` permission for this command")
        else:
            if helper.me.top_role.position <= user.top_role.position:
                await helper.respond(embed=discord.Embed(color=embedColor, title="Error", description=f"Unable to kick `{user}`", timestamp=TIME()).add_field(name="Reason", value="We share the same role or the user's top role is higher than mine"))
                return
            if not helper.author.guild_permissions.moderate_members:
                await helper.respond("You do not have the right permissions for this command")
            else:
                if user.timed_out:
                    await user.remove_timeout(reason=reason)
                    await helper.respond(f"`{user}` was removed from timeout successfully")
                else:
                    await helper.respond(f"`{user}` was not on timeout")


@user_command.command(name="welcome")
@custom_option("gateway", str, autocomplete=create_autocomplete([discord.OptionChoice("server"), discord.OptionChoice("dm")]))
@custom_option("member", discord.Member, name="user")
@custom_option("image", str, default="https://c.tenor.com/w5SAkifVEhUAAAAC/welcome.gif")
@custom_option("message", str, default=None)
async def welcome(ctx: discord.ApplicationContext, member: discord.Member, *, image: str = "https://c.tenor.com/w5SAkifVEhUAAAAC/welcome.gif", message: str = None, gateway: str = "server"):
        if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.PartialMessageable):
            await ctx.respond(embed=UNSUPPORTEDDM)
        else:
            gguild=ctx.guild
            if message==None: message=f"Welcome to **{gguild.name}** dear **{member.name}**"
            if gateway=="server":
                embed=discord.Embed(title="Welcome", description=f"{message}", color=0xFFB6F5)
                embed.set_image(url=image)
                await ctx.send(f"{member.mention}", embed=embed)
                await ctx.respond("Done", ephemeral=True)
            elif gateway=="dm":
                embed=discord.Embed(title="Welcome", description=f"{message}", color=0xFFB6F5)
                embed.set_image(url=image)
                await member.send(embed=embed)
                await ctx.respond("Done", ephemeral=True)
            else:
                embed=discord.Embed(title="Welcome", description=f"{message}", color=0xFFB6F5)
                embed.set_image(url=image)
                await ctx.send(f"{member.mention}", embed=embed)
                await ctx.respond("Done", ephemeral=True)


avatar_command = client.create_group(
    "avatar", "Get the user's avatar")


@avatar_command.command(name="main", description="Get the user's main avatar")
@custom_option("user", **CustomOption(discord.Member, default=None).to_option_dict())
async def main_avatar(ctx: discord.ApplicationContext, user: discord.Member = None):
    helper = Ctx(context=ctx)
    user = user if user else helper.author
    await helper.respond(embed=discord.Embed(color=embedColor, timestamp=TIME()).set_author(name=f"Avatar of {user.display_name}", url=user.avatar).set_image(url=user.avatar))


@avatar_command.command(name="server", description="Get the user's server avatar if possible")
@custom_option("user", **CustomOption(discord.Member, default=None).to_option_dict())
async def server_avatar(ctx: discord.ApplicationContext, user: discord.Member = None):
    helper = Ctx(context=ctx)
    user = user if user else helper.author
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
        return
    avatar = user.guild_avatar if user.guild_avatar else user.display_avatar
    await helper.respond(embed=discord.Embed(color=embedColor, timestamp=TIME(), description="" if user.guild_avatar else "User had no server avatar so the main avatar was given instead").set_author(name=f"Avatar of {user.display_name}", url=avatar).set_image(url=avatar))


@user_command.command(name="unban", description="Unban the specified user from the server [staff only]")
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
@custom_option("user_id", **CustomOption(int).to_option_dict())
async def user_unban(ctx: discord.ApplicationContext, user_id: int, reason: str = None):
    helper = Ctx(context=ctx)
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.ban_members:
            await helper.respond("I require the `ban members` permission for this command")
        else:
            if not helper.author.guild_permissions.ban_members:
                await helper.respond("You do not have the right permissions for this command")
            else:
                user = await client.fetch_user(user_id)
                await helper.guild.unban(user, reason=reason)
                await helper.respond("User was unbanned successfully")


role_command = client.create_group(
    "role", "This command group has the subcommands for working with roles")


@role_command.command(name="info", description="Get info about the specified role")
@custom_option("role", **CustomOption(discord.Role).to_option_dict())
async def role_info(ctx: discord.ApplicationContext, role: discord.Role):
    helper = Ctx(context=ctx)
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        await helper.respond(embed=discord.Embed(color=embedColor, title="Role Info", description=f"""**Name**: {role.name}
**Color/Colour**: {role.color}
**Id**: {role.id}
**Icon**: [Icon]({role.icon})
**Mentionable**: {"On" if role.mentionable else "Off"}
**Members**: {len(role.members)}
**Creation Date**: {discord_time_formatter(role.created_at, "F")}""", timestamp=TIME()))


@role_command.command(name="create", description="Create a new role [staff only]")
@custom_option("name", **CustomOption(str).to_option_dict())
@custom_option("color", **CustomOption(str, description="A hex value for the role color", default="000000").to_option_dict())
@custom_option("mentionable", **CustomOption(bool, default=True).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def role_create(ctx: discord.ApplicationContext, name: str, color: str = "000000", mentionable: bool = True, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.manage_roles:
            await helper.respond("I require `manage roles` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_roles:
                await helper.respond("You do not have the right permissions for this command")
            else:
                role = await helper.guild.create_role(reason=reason, name=name, mentionable=mentionable, color=int(color, base=16))
                await helper.respond(f"Role was successfully created - {role.mention}")


@role_command.command(name="delete", description="Delete the specified role [staff only]")
@custom_option("role", **CustomOption(discord.Role).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def delete_role(ctx: discord.ApplicationContext, role: discord.Role, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.manage_roles:
            await helper.respond("I require `manage roles` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_roles:
                await helper.respond("You do not have the right permissions for this command")
            else:
                await role.delete(reason=reason)
                await helper.respond("Role was successfully deleted")


@role_command.command(name="add", description="Add the specified to a user [staff only]")
@custom_option("role", **CustomOption(discord.Role).to_option_dict())
@custom_option("user2", **CustomOption(discord.Member, default=None).to_option_dict())
@custom_option("user3", **CustomOption(discord.Member, default=None).to_option_dict())
@custom_option("user1", **CustomOption(discord.Member).to_option_dict())
async def add_role(ctx: discord.ApplicationContext, role: discord.Role, user1: discord.Member, user2: discord.Member = None, user3: discord.Member = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.manage_roles:
            await helper.respond("I require `manage roles` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_roles:
                await helper.respond("You do not have the right permissions for this command")
            else:
                success = "\n"
                s = []
                if user1.top_role.position <= helper.me.top_role.position:
                    s.append(f"Adding role to `{user1}` failed")
                else:
                    if not role in user1.roles:
                        await user1.add_roles(role)
                        s.append(f"Adding role to `{user1}` succeded")
                    else:
                        s.append(f"`{user1}` already has the role")
                if user2:
                    if user2.top_role.position <= helper.me.top_role.position:
                        s.append(f"Adding role to `{user2}` failed")
                    else:
                        if not role in user2.roles:
                            await user2.add_roles(role)
                            s.append(f"Adding role to `{user2}` succeded")
                        else:
                            s.append(f"`{user2}` already has the role")
                if user3:
                    if user3.top_role.position <= helper.me.top_role.position:
                        s.append(f"Adding role to `{user3}` failed")
                    else:
                        if not role in user3.roles:
                            await user3.add_roles(role)
                            s.append(f"Adding role to `{user3}` succeded")
                        else:
                            s.append(f"`{user3}` already has the role")
                await helper.respond(success.join(s))


emoji_command = client.create_group(
    "emoji", "This command group has the subcommands for working with emojis")


@emoji_command.command(name="info", description="Info about the specified emoji if possible")
@custom_option("emoji", **CustomOption(str).to_option_dict())
async def emoji_info(ctx: discord.ApplicationContext, emoji: str):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        try:
            emoji_ = await helper.guild.fetch_emoji(int(emoji.split("<")[1].split(">")[0].split(":")[2]))
        except IndexError:
            await helper.respond("Emoji must be a server emoji not a default one")
            return
        await helper.respond(embed=discord.Embed(color=embedColor, title="Emoji Info", description=f"""**Name**: {emoji_.name}
**Id**: {emoji_.id}
**Animated**: {"Yes" if emoji_.animated else "No"}
**Icon**: [Icon]({emoji_.url})
**Creation Date**: {discord_time_formatter(emoji_.created_at, "F")}""", timestamp=TIME()).set_thumbnail(url=emoji_.url))


@emoji_command.command(name="create", description="Create a new emoji [staff only]")
@custom_option("name", **CustomOption(str).to_option_dict())
@custom_option("icon", **CustomOption(discord.Attachment).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def emoji_create(ctx: discord.ApplicationContext, name: str, icon: discord.Attachment, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.manage_emojis:
            await helper.respond("I require `manage emojis` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_emojis:
                await helper.respond("You do not have the right permissions for this command")
            else:
                try:
                    emoji = await helper.guild.create_custom_emoji(name=name, image=await icon.read(), reason=reason)
                except:
                    await helper.respond("The file was to large!")
                    return
                await helper.respond(f"Emoji was created successfully - {emoji}")


@emoji_command.command(name="edit", description="Edit the specified emoji [staff only]")
@custom_option("name", **CustomOption(str).to_option_dict())
@custom_option("emoji", **CustomOption(str).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def emoji_edit(ctx: discord.ApplicationContext, emoji: str, name: str, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.manage_emojis:
            await helper.respond("I require `manage emojis` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_emojis:
                await helper.respond("You do not have the right permissions for this command")
            else:
                try:
                    emoji_ = await helper.guild.fetch_emoji(int(emoji.split("<")[1].split(">")[0].split(":")[2]))
                except IndexError:
                    await helper.respond("Emoji must be a server emoji not a default one")
                    return
                await emoji_.edit(name=name)
                await helper.respond("Emoji was updated successfully")


@emoji_command.command(name="delete", description="Delete the specified emoji [staff only]")
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
@custom_option("emoji", **CustomOption(str).to_option_dict())
async def emoji_delete(ctx: discord.ApplicationContext, emoji: str, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.manage_emojis:
            await helper.respond("I require `manage emojis` permission for this command")
        else:
            if not helper.author.guild_permissions.manage_emojis:
                await helper.respond("You do not have the right permissions for this command")
            else:
                try:
                    emoji_ = await helper.guild.fetch_emoji(int(emoji.split("<")[1].split(">")[0].split(":")[2]))
                except IndexError:
                    await helper.respond("Emoji must be a server emoji not a default one")
                    return
                await emoji_.delete(reason=reason)
                await helper.respond("Emoji was deleted successfully")


@client.command(name="thread", description="Start a new thread")
@custom_option("name", **CustomOption(str).to_option_dict())
@custom_option("channel", **CustomOption(discord.TextChannel, default=None).to_option_dict())
@custom_option("mention_me", **CustomOption(bool, default=False).to_option_dict())
@custom_option("reason", **CustomOption(str, default=None).to_option_dict())
async def thread(ctx: discord.ApplicationContext, name: str, channel: discord.TextChannel = None, mention_me: bool = False, reason: str = None):
    helper = Ctx(context=ctx)
    await helper.defer()
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.me.guild_permissions.create_public_threads:
            await helper.respond("I require `create public thread` and `send messages in threads` permission for this command")

        else:
            if not helper.author.guild_permissions.create_public_threads:
                await helper.respond("You do not have the right permissions for this command")
            else:
                channel = channel if channel else helper.channel
                thread = await channel.create_thread(name=name, type=discord.ChannelType.public_thread, auto_archive_duration=channel.default_auto_archive_duration, reason=reason)
                await helper.respond(thread.mention)
                if mention_me:
                    if helper.me.guild_permissions.send_messages_in_threads:
                        await thread.send(helper.author.mention)
                    else:
                        await helper.respond("i require `send messages in threads` permissio to mention you")


@client.command(name="announce", description="Announce the latest news about the server")
@custom_option("title", **CustomOption(str).to_option_dict())
@custom_option("message", **CustomOption(str, description="Use %^ for new lines").to_option_dict())
@custom_option("channel", **CustomOption(discord.TextChannel).to_option_dict())
@custom_option("mention_role", **CustomOption(discord.Role, default=None).to_option_dict())
@custom_option("image", **CustomOption(discord.Attachment, default=None).to_option_dict())
async def announce(ctx: discord.ApplicationContext, title: str, message: str, channel: discord.TextChannel, mention_role: discord.Role = None, image: discord.Attachment = None):
    helper = Ctx(context=ctx)
    if isinstance(helper.channel, discord.PartialMessageable):
        await helper.respond(embed=UNSUPPORTEDDM)
        return
    if not helper.author.guild_permissions.advanced:
        await helper.respond("You do not have the right permissions for this command!")
        return
    embed = discord.Embed(color=embedColor, title="__"+title+"__", description=message.replace("%^", "\n")
                          ).set_footer(text=f"Announcement by {helper.author}", icon_url=helper.author.display_avatar)
    if image:
        embed.set_image(url=image.url)
        d = await client.fetch_channel(937051423286394893)
        await d.send(f";{image.url};", file=await image.to_file())

    class btn1(discord.ui.Button):
        def __init__(self):
            super().__init__(style=discord.ButtonStyle.green, label="Send", emoji="📤")

        async def callback(self, interaction: discord.Interaction):
            ctxx = Ctx(interaction=interaction, bot=client)
            if mention_role:
                msg = await channel.send(mention_role.mention, embed=embed)
            else:
                msg = await channel.send(embed=embed)
            await ctxx.edit_message(content=f"[Announcement]({msg.jump_url})", embed=None, view=None)

    class btn2(discord.ui.Button):
        def __init__(self):
            super().__init__(style=discord.ButtonStyle.red, label="Delete", emoji="🗑️")

        async def callback(self, interaction: discord.Interaction):
            ctxx = Ctx(interaction=interaction, bot=client)
            await ctxx.edit_message(content=f"Announcement deleted", embed=None, view=None)
    view = create_view([btn1(), btn2()])
    w = await helper.respond("**Preview**", embed=embed, view=view)


reddit_command = client.create_group(
    "reddit", "Get a post from any subreddit given, if you can't find it then use the search subcommand")


@reddit_command.command(name="hentai", description="Get a random post from the hentai subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_hentai(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR, ephemeral=True)
    else:
        post = Reddit.get_reddit_posts("hentai").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts("hentai").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="porn", description="Get a random post from the adorableporn subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_porn(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR, ephemeral=True)
    else:
        post = Reddit.get_reddit_posts("adorableporn").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "adorableporn").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="cosplay", description="TGet a random post from the cosplaygirls subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_cosplay(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR, ephemeral=True)
    else:
        post = Reddit.get_reddit_posts("cosplaygirls").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "cosplaygirls").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="search", description="Get a post from any subreddit if available")
@custom_option("subreddit", **CustomOption(str).to_option_dict())
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_search(ctx: discord.ApplicationContext, subreddit: str, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    post = Reddit.get_reddit_posts(subreddit).random_post
    if post.over_18 and not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, url=post.shortlink, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes} {'' if not post.over_18 else '• Nsfw'}").set_image(url=post.url))


@reddit_command.command(name="hentaibdsm", description="Get a random post from the hentaibondage subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_bdsm(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        post = Reddit.get_reddit_posts("hentaibondage").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "hentaibondage").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="feet", description="Get a random post from the AnimeFeets subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_feet(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        post = Reddit.get_reddit_posts("AnimeFeets").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "AnimeFeets").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="ecchi", description="Get a random post from the ecchi subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_ecchi(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        post = Reddit.get_reddit_posts("ecchi").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "ecchi").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="genshinhentai", description="Get a random post from the GenshinImpactHentai subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_genshin_hentai(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        post = Reddit.get_reddit_posts("GenshinImpactHentai").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "GenshinImpactHentai").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="yuri", description="Get a random post from the yuri subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_yuri(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        post = Reddit.get_reddit_posts("yuri").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "yuri").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


@reddit_command.command(name="yaoi", description="Get a random post from the yaoi subreddit")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def reddit_yaoi(ctx, private: bool = False):
    helper = Ctx(context=ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        post = Reddit.get_reddit_posts("yaoi").random_post

        class btn(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.blurple, label="One more", row=1)
                self.count = 1

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    pass
                elif self.count == 10:
                    self.disabled = True
                else:
                    new_post = Reddit.get_reddit_posts(
                        "yaoi").random_post
                    await interaction.response.defer(ephemeral=private)
                    await interaction.followup.send(embed=discord.Embed(title=new_post.title, color=embedColor, timestamp=TIME()).set_image(url=new_post.url).set_footer(text=f"Upvotes: {new_post.upvotes}"), view=create_view([
                        discord.ui.Button(
                            style=discord.ButtonStyle.url, label="Photo", url=new_post.url, emoji="🖼️", row=0),
                        discord.ui.Button(style=discord.ButtonStyle.url, label="Post", url=new_post.shortlink, emoji=reddit_logo, row=0), self], None))
                    self.count += 1
                    if self.count == 10:
                        self.disabled = True
        await helper.respond(embed=discord.Embed(color=embedColor, title=post.title, timestamp=TIME()).set_footer(text=f"Upvotes: {post.upvotes}").set_image(url=post.url), view=create_view([
            discord.ui.Button(style=discord.ButtonStyle.url,
                              label="Photo", url=post.url, emoji="🖼️", row=0),
            discord.ui.Button(style=discord.ButtonStyle.url, label="Post",
                              url=post.shortlink, emoji=reddit_logo, row=0),
            btn()
        ], None))


autocmpl = create_autocomplete([discord.OptionChoice(
    "meme"), discord.OptionChoice("animememe"), discord.OptionChoice("hentaimeme")])


@reddit_command.command(name="memes", description="Reddit memes")
@custom_option("type_", str, name="type", default="meme", autocomplete=autocmpl)
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
async def meme(ctx: discord.ApplicationContext, type_: str = "meme", private: bool = False):
    helper = Ctx.from_context(ctx)
    await helper.defer(ephemeral=private)
    type_ += 's'
    post = Reddit.get_reddit_posts(type_).random_post
    if type_ == "hentaimemes" and not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
    else:
        embed = discord.Embed(color=embedColor, title=post.title, timestamp=TIME(
        )).set_image(url=post.url).set_footer(text=f"Upvotes: {post.upvotes}")
        await helper.respond(embed=embed, view=create_view([discord.ui.Button(style=discord.ButtonStyle.url, label="Source", url=post.shortlink, emoji=reddit_logo)]))


@client.command(name="yandere", description="Get a nsfw photo from yande.re")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
@custom_option("tag1", **CustomOption(str, default=None).to_option_dict())
@custom_option("tag2", **CustomOption(str, default=None).to_option_dict())
@custom_option("tag3", **CustomOption(str, default=None).to_option_dict())
async def yandere_(ctx: discord.ApplicationContext, tag1: str = None, tag2: str = None, tag3: str = None, private: bool = False):
    helper = Ctx.from_context(ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
        return
    try:
        yandere = Yandere([tag1, tag2, tag3], limit=100, explicit=True)
    except YandereConfig.ForbiddenTagError as error:
        await helper.respond(error.args[0].replace("'", "`"))
        return
    except JSONDecodeError:
        await helper.respond("Couldn't find a post with those tags")
        return
    post = yandere.random_post
    embed = discord.Embed(color=embedColor, description=f"**{f'[Source]({post.source})' if post.source else 'Source'} | [Post]({post.post_url}) | [File]({post.file_url})**", timestamp=TIME(
    )).set_image(url=post.file_url).set_footer(text=f"From yande.re • Id: {post.id}")
    await helper.respond(embed=embed)


@client.command(name="danbooru", description="Get a nsfw photo from danbooru")
@custom_option("private", **CustomOption(bool, default=False).to_option_dict())
@custom_option("tag1", **CustomOption(str, default=None).to_option_dict())
@custom_option("tag2", **CustomOption(str, default=None).to_option_dict())
@custom_option("tag3", **CustomOption(str, default=None).to_option_dict())
async def danbooru_(ctx: discord.ApplicationContext, tag1: str = None, tag2: str = None, tag3: str = None, private: bool = False):
    helper = Ctx.from_context(ctx)
    await helper.defer(ephemeral=private)
    if not helper.nsfw:
        await helper.respond(embed=NSFWERROR)
        return
    try:
        Source = "source"
        post = danbooru(
            *[tag for tag in [tag1, tag2, tag3] if isinstance(tag, str)])
        embed = discord.Embed(color=embedColor, description=f"**{'[Source]('+post[Source]+')' if post[Source] != '' else 'Source'} | {'[Post](https://danbooru.donmai.us/posts/'+str(post['id'])+')'} | [File]({post['file_url']})**", timestamp=TIME(
        )).set_image(url=post["file_url"]).set_footer(text=f"From danbooru • Id: {str(post['id'])}")
        await helper.respond(embed=embed)
    except:
        await helper.respond("Getting post failed")


bot_command = client.create_group("bot")


@bot_command.command(name="feedback", description="Send feedback")
async def feedback(ctx: discord.ApplicationContext):
    helper = Ctx.from_context(ctx)

    class feedbackmodal(discord.ui.Modal):
        def __init__(self) -> None:
            super().__init__(title="Feedback")
            self.add_item(discord.ui.InputText(
                style=discord.InputTextStyle.long, label="Feedback about me", placeholder="Feedback"))

        async def callback(self, interaction: discord.Interaction):
            feedbackchannel = client.fetch_channel(977967584836206642)
            if isinstance(interaction.channel, discord.PartialMessageable) or isinstance(interaction.channel, discord.DMChannel):
                await feedbackchannel.send(embed=discord.Embed(color=embedColor, title="Feedback", description=self.children[0].value).add_field(name="From", value=f"User: **``{ctx.user}``**\nServer: **``[DM]``**"))
                await interaction.response.send_message("Thank you for the feedback!\nIf you need any help you can join the support server!", ephemeral=True)
            else:
                await feedbackchannel.send(embed=discord.Embed(color=embedColor, title="Feedback", description=self.children[0].value).add_field(name="From", value=f"User: **``{ctx.user}``**\nServer: **``{ctx.guild.name}``**"))
                await interaction.response.send_message("Thank you for the feedback!\nIf you need any help you can join the support server!", ephemeral=True)
    await helper.send_modal(feedbackmodal())


@bot_command.command(name="reportproblem", description="Report any problem that you had while using the bot")
async def report_problem(ctx: discord.ApplicationContext):
    class Modall(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Report a problem")
            self.add_item(discord.ui.InputText(style=discord.InputTextStyle.short, label="Command",
                          placeholder="The command that has the problem", required=False))
            self.add_item(discord.ui.InputText(style=discord.InputTextStyle.long, label="Problem",
                          placeholder="The description of the problem", required=True))

        async def callback(self, interaction: discord.Interaction):
            if isinstance(interaction.channel, discord.PartialMessageable):
                embed = discord.Embed(color=embedColor, title="Problem", description=self.children[1].value).add_field(
                    name="Command", value=f"`{self.children[0].value}`", inline=False).add_field(name="From", value=f"User: **`{ctx.author}`**\nServer: **`[Dm]`**", inline=False)
                channel = client.get_channel(977967690327154708)
                await channel.send(embed=embed)
                await interaction.response.send_message("Problem submitted", ephemeral=True)
            else:
                embed = discord.Embed(color=embedColor, title="Problem", description=self.children[1].value).add_field(
                    name="Command", value=f"`{self.children[0].value}`", inline=False).add_field(name="From", value=f"User: **`{ctx.author}`**\nServer: **`{ctx.guild.name}`**", inline=False)
                channel = client.get_channel(977967690327154708)
                await channel.send(embed=embed)
                await interaction.response.send_message("Problem submitted", ephemeral=True)

    helper = Ctx.from_context(ctx)
    await helper.send_modal(Modall())


@bot_command.command(name="suggest", description="Suggest a command")
@custom_option("command", **CustomOption(str).to_option_dict())
@custom_option("description", **CustomOption(str).to_option_dict())
async def bot_suggest(ctx: discord.ApplicationContext, command: str, description: str):
    helper = Ctx.from_context(ctx)
    channel = await client.fetch_channel(977971046349176852)
    await channel.send(embed=discord.Embed(color=embedColor, title="Command: "+command, description="**Description**: "+description).set_author(name="From "+helper.author.__str__()))
    await helper.respond("Suggestion sent, thank you!", ephemeral=True)


@bot_command.command(name="vote", description="Voting is optional")
async def vote(ctx: discord.ApplicationContext):
    button = discord.ui.Button(
        style=discord.ButtonStyle.url, label="Vote", url=vote_link)
    view = discord.ui.View(timeout=0)
    view.add_item(button)
    await ctx.respond(embed=discord.Embed(title="Vote for me here!", url=vote_link, description="Voting won't change anything, so it isn't required, but you can vote to help the bot grow!", color=embedColor), view=view)


games_command = client.create_group("games")


self_choices = ["rock", "paper", "scissors"]


async def get_choices(ctx: discord.AutocompleteContext):
    return [choice for choice in self_choices if choice.startswith(ctx.value.lower())]


@games_command.command(name="rps", description="rock/paper/scissors")
@custom_option("choice", str, autocomplete=get_choices)
async def rps(ctx: discord.ApplicationContext, choice: str):
    self_choice = random.choice(self_choices)

    if self_choice == "rock" and choice == "rock":
        await ctx.respond(f"My choice was **rock**\nYour choice was **rock**\n**It is a draw**!")

    elif self_choice == "rock" and choice == "paper":
        await ctx.respond(f"My choice was **rock**\nYour choice was **paper**\n**You win**!")

    elif self_choice == "rock" and choice == "scissors":
        await ctx.respond(f"My choice was **rock**\nYour choice was **scissors**\n**I win**!")

    elif self_choice == "paper" and choice == "rock":
        await ctx.respond(f"My choice was **paper**\nYour choice was **rock**\n**I win**!")

    elif self_choice == "paper" and choice == "paper":
        await ctx.respond(f"My choice was **paper**\nYour choice was **paper**\n**It is a draw**!")

    elif self_choice == "paper" and choice == "scissors":
        await ctx.respond(f"My choice was **paper**\nYour choice was **scissors**\n**You win**!")

    elif self_choice == "scissors" and choice == "rock":
        await ctx.respond(f"My choice was **scissors**\nYour choice was **rock**\n**You win**!")

    elif self_choice == "scissors" and choice == "paper":
        await ctx.respond(f"My choice was **scissors**\nYour choice was **paper**\n**I win**!")

    elif self_choice == "scissors" and choice == "scissors":
        await ctx.respond(f"My choice was **scissors**\nYour choice was **scissors**\n**It is a draw**!")


def random_number_generator(range_: int):
    numberNumber: int = random.randint(1, range_)
    return numberNumber


dice_types = ["1-6", "1-20", "other_choice"]


async def get_dice_types(ctx: discord.AutocompleteContext):
    return [dice_type for dice_type in dice_types if dice_type.startswith(ctx.value.lower())]


@games_command.command(description="Roll a die")
@custom_option("dice_type", str, autocomplete=get_dice_types, default="1-6")
@custom_option("other_choice", int, default=None)
async def dice(ctx: discord.ApplicationContext, dice_type: str = "1-6", other_choice: int = None):
    if dice_type == "1-6":
        dice = random_number_generator(6)
        await ctx.respond(f"You rolled **{dice}**!")
    elif dice_type == "1-20":
        dice = random_number_generator(20)
        await ctx.respond(f"You rolled **{dice}**!")
    elif dice_type == "other_choice" and other_choice == None:
        await ctx.respond("Please specify the ``other_choice``!")
    elif dice_type == "other_choice" and other_choice is not None:
        dice = random_number_generator(other_choice)
        await ctx.respond(f"You rolled **{dice}**!")


magicball = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.",
             "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]


@games_command.command(description="Ask a question and the magic 8 ball will answer it")
@custom_option("question", str)
async def magic8ball(ctx: discord.ApplicationContext, question: str):
    if not question.endswith("?"):
        question = f"{question}?"
    await ctx.defer(ephemeral=False)
    await asyncio.sleep(2)
    answer = random.choice(magicball)
    embed = discord.Embed(color=embedColor, description=f"Your question: **{question}**\nAnswer: **{answer}**").set_author(
        name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
    await ctx.respond(embed=embed)


coinautocmp = create_autocomplete(
    [discord.OptionChoice("heads"), discord.OptionChoice("tails")])


@games_command.command(description="Flip a coin")
@custom_option("arg1", str, name="bet", description="Bet on the coin", default=None, autocomplete=coinautocmp)
async def coinflip(ctx: discord.ApplicationContext, arg1: str = None):
    await ctx.defer()
    await asyncio.sleep(2)
    face = random.choice([f"{heads}", f"{tails}"])
    if not arg1 == None:
        embed = discord.Embed(title="Coin flip", description=f"You bet on **{arg1}**", color=embedColor).add_field(
            name="Flip result", value=face, inline=False).set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)
        if arg1 == "heads" and face == heads:
            embed.add_field(name="Bet result",
                            value="You won the bet!", inline=False)
            await ctx.respond(embed=embed)
        elif arg1 == "tails" and face == tails:
            embed.add_field(name="Bet result",
                            value="You won the bet!", inline=False)
            await ctx.respond(embed=embed)
        else:
            embed.add_field(name="Bet result",
                            value="You lost the bet!", inline=False)
            await ctx.respond(embed=embed)
    else:
        await ctx.respond(content=face)


math_command = client.create_group("math")


@math_command.command(name="add", description="Add two numbers together")
@custom_option("number1", float)
@custom_option("number2", float)
async def math_add(ctx: discord.ApplicationContext, number1: float, number2: float):
    await ctx.respond(f"**Result**: {number1 + number2}")


@math_command.command(name="subtract", description="Subtract number2 from number1")
@custom_option("number1", float)
@custom_option("number2", float)
async def math_sub(ctx: discord.ApplicationContext, number1: float, number2: float):
    await ctx.respond(f"**Result**: {number1 - number2}")


@math_command.command(name="multiply", description="Multiply two numbers")
@custom_option("number1", float)
@custom_option("number2", float)
async def math_mul(ctx: discord.ApplicationContext, number1: float, number2: float):
    await ctx.respond(f"**Result**: {number1 * number2}")


@math_command.command(name="divide", description="Divide two numbers")
@custom_option("number1", float)
@custom_option("number2", float)
async def math_div(ctx: discord.ApplicationContext, number1: float, number2: float):
    await ctx.respond(f"**Result**: {number1 / number2}")


@math_command.command(name="power", description="Raise number1 to the power of number2")
@custom_option("number1", float)
@custom_option("number2", int)
async def math_pow(ctx: discord.ApplicationContext, number1: float, number2: int):
    await ctx.respond(f"**Result**: {number1 ** number2}")


sayautocmp = create_autocomplete(
    [discord.OptionChoice("bot"), discord.OptionChoice("webhook")])


@client.command(description="Say something in the chat")
@custom_option("message", str, description="Use ^ for a new line")
@custom_option("way", str, autocomplete=sayautocmp, default="bot")
async def say(ctx: discord.ApplicationContext, message: str, way: str = "bot"):
    if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.PartialMessageable):
        await ctx.respond(embed=UNSUPPORTEDDM)
    else:
        if way == "bot":
            msg = message.replace("^", "\n")
            await ctx.respond("done", ephemeral=True)
            emm = discord.Embed(color=0xFFb6F5, description=f"{msg}")
            emm.set_author(name=f"{ctx.user.display_name} says:",
                           icon_url=ctx.user.display_avatar)
            await ctx.send(embed=emm)
        else:
            try:
                msg = message.replace("^", "\n")
                await ctx.respond("done", ephemeral=True)
                emm = discord.Embed(color=ctx.author.color, title=f"{msg}")
                webh = ctx.interaction.channel.create_webhook(name=f"{ctx.author.display_name}", avatar=await ctx.author.display_avatar.read())
                w = await webh
                await w.send(embed=emm)
                await w.delete()
            except:
                msg = message.replace("^", "\n")
                emm = discord.Embed(color=0xFFb6F5, description=f"{msg}")
                emm.set_author(name=f"{ctx.user.display_name} says:",
                               icon_url=ctx.user.display_avatar)
                await ctx.send(embed=emm)


async def clear(ctx: discord.ApplicationContext, amount: int = 2):
    if isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.PartialMessageable):
        await ctx.respond(embed=UNSUPPORTEDDM)
    else:
        q = int(amount)
        if not ctx.author.guild_permissions.manage_messages:
            embed1 = discord.Embed(
                description=f"{xx} - You don't have permission to use this command!", color=0xFFB6F5)
            msgg = await ctx.respond(embed=embed1)
            await asyncio.sleep(10)
            # await ctx.channel.purge(limit=1)
            await msgg.delete_original_message()
        else:
            if int(q) > 1000:
                await ctx.respond("I am not able to clear this many messages", ephemeral=True)
            else:
                mssg = await ctx.respond("alright deleting!")
                await asyncio.sleep(2)
                await mssg.delete_original_message()
                await ctx.channel.purge(limit=q)
                embed2 = discord.Embed(
                    description=f"{check} - {q} messages were deleted from the channel!", color=0xFFB6F5, timestamp=datetime.datetime.now())
                embed2.set_footer(
                    text=f"This message will be removed in 10 seconds")
                msg = await ctx.send(embed=embed2)
                await asyncio.sleep(10)
                # await ctx.channel.purge(limit=1)
                await msg.delete()


@client.command(name="clear", description="Clear an amount of messages")
@custom_option("amount", int, default=5, max_value=1000)
@custom_option("user_id", int, default=None)
async def clear_(ctx: discord.ApplicationContext, amount: int = 5, user_id=None):
    helper = Ctx.from_context(ctx)
    if isinstance(helper.channel, discord.DMChannel) or isinstance(helper.channel, discord.PartialMessageable):
        await ctx.respond(embed=UNSUPPORTEDDM)
    else:
        if not helper.guild.me.guild_permissions.manage_messages:
            await helper.respond("I require the `manage messages` permission for this command")
        amount1 = amount
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.respond("You do not have the right permissions to use this command!")
        else:
            if user_id == None:
                await clear(ctx, amount)
                return
            w = await ctx.respond("Command ready")
            await asyncio.sleep(2)
            await w.delete_original_message()
            history = await helper.channel.history(limit=1000000, oldest_first=False).flatten()
            number = 0
            for message in history:
                if message.author.id == int(user_id):
                    if number == amount1:
                        break
                    else:
                        number = number+1
                    await message.delete()
                else:
                    pass
            msg = await helper.send(embed=discord.Embed(color=embedColor, description=f"{check} - {number-1} messages were deleted"))
            await asyncio.sleep(5)
            await msg.delete()


hugs = ["https://tenor.com/view/teria-wang-kishuku-gakkou-no-juliet-hug-anime-gif-16509980", "https://tenor.com/view/horimiya-hug-anime-miyamura-hori-gif-20848980",
        "https://tenor.com/view/hug-gif-24003809", "https://tenor.com/view/hug-anime-gif-19674744", "https://tenor.com/view/anime-hug-anime-hug-gif-24791513"]


#action_command = client.create_group("action")


#@action_command.command(name="hug", decsription="Hug someone")
#@custom_option("user", discord.Member, default=None)
async def action_hug(ctx: discord.ApplicationContext, user: discord.Member = None):
    await ctx.defer()
    helper = Ctx.from_context(ctx)
    if user == None: user = helper.author
    if not helper.author == user:
        await helper.respond(f"**{helper.author.display_name}** [hugs]({random.choice(hugs)}) {user.mention}")
    else:
        await helper.respond(f"**{helper.guild.me.display_name}** [hugs]({random.choice(hugs)}) {user.mention}")



#@action_command.command(name="marry")
#@custom_option("member", discord.Member, name="user")
async def marry(ctx: discord.ApplicationContext, member:discord.Member):
    if isinstance(ctx.channel, discord.PartialMessageable):
        await ctx.respond(embed=UNSUPPORTEDDM)
        return
    hh=random.choice(hhh)
    embed=discord.Embed(title='New marriage', description=f"So cute, **{ctx.author.display_name}** and **{member.display_name}** are getting married!", color=0xFFB6F5)
    embed.set_image(url=hh)
    embed.set_footer(text="I wish you two a happy life!", icon_url="https://cdn.discordapp.com/avatars/891397139547185153/7ad9cb00be8c484d7aa1ab06489ebdfb.png?size=1024")
    await ctx.respond(embed=embed)


from helpcmd import helper
helper(client)


client.run("Token")
