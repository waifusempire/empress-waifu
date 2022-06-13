import datetime
import asyncio
from dis import dis
from enum import Enum
from typing import Any, Awaitable, Callable, ClassVar, Coroutine, overload
from discord.commands.core import Option
import discord
from discord import MISSING, ApplicationContext, Attachment, AutocompleteContext, Bot, CategoryChannel, Interaction, Member, OptionChoice, PartialMessageable, Role, StageChannel, TextChannel, Thread, User, VoiceChannel


ModalLike = discord.ui.Modal


class MissingOptionValue:
    def __init__(self, value):
        self.__value = value

    def __eq__(self, other):
        if isinstance(other, type(self)):
            if other._MissingOptionValue__value == self.__value:
                return True
            else:
                return False
        else:
            return False

    def __repr__(self):
        return "MissingOptionValue['{value}']".format(value=self.__value)


class DefaultOptionValue:
    def __new__(cls, value):
        return value


SlashCommandInputType = str | int | float | bool | Role | TextChannel | VoiceChannel | User | Member | Attachment
InteractionChannel = discord.VoiceChannel | discord.StageChannel | discord.TextChannel | discord.CategoryChannel | discord.Thread | discord.PartialMessageable


class CustomOption:
    def __init__(self, input_type: SlashCommandInputType, name: str = DefaultOptionValue(None), description: str = DefaultOptionValue(None), default: Any = MissingOptionValue("default"), max_value: int = DefaultOptionValue(None), min_value: int = DefaultOptionValue(None), autocomplete: bool = DefaultOptionValue(False)):
        self.name = name
        self.description = description
        self.required = True if default == MissingOptionValue(
            "default") else False
        self.default = default if not default == MissingOptionValue(
            "default") else None
        self.min_value = min_value
        self.max_value = max_value
        self.input_type = input_type
        self.choices: list[OptionChoice | None] = []
        self._should_autocomplete = autocomplete
        self.autocomplete = None

    def add_choice(self, name: str, value: str | int | float = None):
        self.choices.append(OptionChoice(name, value))
        return self

    def build_autocomplete(self):
        if self._should_autocomplete:
            safe_choices = [
                choice for choice in self.choices if isinstance(choice, OptionChoice)]

            async def autocompletewrapper(ctx: AutocompleteContext):
                return [choice for choice in safe_choices if choice.name.startswith(ctx.value.lower())]
            self.autocomplete = autocompletewrapper
            return self
        else:
            return self
        
    def to_option(self):
        return Option(self.input_type, name=self.name, description=self.description, choices=self.choices, required=self.required, default=self.default, min_value=self.min_value, max_value=self.max_value, autocomplete=self.autocomplete)

    def to_dict(self):
        return dict(input_type=self.input_type, name=self.name, description=self.description, choices=self.choices, required=self.required, default=self.default, min_value=self.min_value, max_value=self.max_value, autocomplete=self.autocomplete)

    def to_option_dict(self):
        return dict(type=self.input_type, name=self.name, description=self.description, choices=self.choices, required=self.required, default=self.default, min_value=self.min_value, max_value=self.max_value, autocomplete=self.autocomplete)


def create_autocomplete(choices: list[OptionChoice]):
    async def autocompletewrapper(ctx: AutocompleteContext):
        return [choice for choice in choices if choice.name.startswith(ctx.value.lower())]
    return autocompletewrapper


def custom_option(name_: str, type: SlashCommandInputType = None, **kwargs):
    """A decorator that can be used instead of typehinting Option"""

    def decorator(func: Awaitable[Callable[..., None]]):
        nonlocal type
        type = type or func.__annotations__.get(name_, str)
        func.__annotations__[name_] = Option(type, **kwargs)
        return func

    return decorator


def create_view(items: list[discord.ui.Item], timeout: float | None = 180) -> discord.ui.View:
    view = discord.ui.View(timeout=timeout)
    for item in items:
        view.add_item(item=item)
    return view


def discord_time_formatter(time: datetime.datetime | float | None = None, time_format: str = "t"):
    """If time is `None`, it get's the current time\n
`"R"` - Relative Time\n
`"t"` - Short Time\n
`"T"` - Long Time\n
`"d"` - Short Date\n
`"D"` - Long Date\n
`"f"` - Short Date/Time\n
`"F"` - Long Date/Time\n
For more info check here <https://c.r74n.com/discord/formatting#Timestamps>"""

    import time as time_manager

    if time == None:
        time = int(time_manager.time())
    if isinstance(time, datetime.datetime):
        return "<t:"+str(int(time.timestamp()))+f":{time_format}>"
    elif isinstance(time, float):
        return "<t:"+str(int(time))+f":{time_format}>"
    elif isinstance(time, int):
        return "<t:"+str(time)+f":{time_format}>"
    else:
        raise TypeError(
            "'time' can only be of the types float or datetime")


class ContextHelper:

    @overload
    def __init__(self, *, context: ApplicationContext):
        '''Parameters
---------
context: `ApplicationContext`\n
Attributes
----------\n
context: `ApplicationContext`
interaction: `Interaction`
bot: `Bot`
command: `ApplicationCommand`
cog: `Cog`'''
        ...

    @overload
    def __init__(self, *, interaction: Interaction, bot: Bot):
        '''Parameters
---------
interaction: `Interaction`\n
bot: `Bot`\n
Attributes
----------\n
context: `ApplicationContext`
interaction: `Interaction`
bot: `Bot`
command: `ApplicationCommand`
cog: `Cog`'''
        ...

    def __init__(self, *, context: ApplicationContext = None, interaction: Interaction = None, bot: Bot = None):
        if context:
            if isinstance(context, ApplicationContext):
                self.context = context
                self.interaction = context.interaction
                self.bot = context.bot
                self.command = context.command
                self.cog = context.cog
                self.user = self.interaction.user
            else:
                raise TypeError(
                    "context must be of the type[ApplicationContext]")
        else:
            if not isinstance(interaction, Interaction) and not isinstance(bot, Bot):
                raise TypeError(
                    "interaction must only be of type 'Interaction' and bot must only be of type 'Bot'")
            elif not isinstance(interaction, Interaction):
                raise TypeError(
                    "interaction must only be of type 'Interaction'")
            elif not isinstance(bot, Bot):
                raise TypeError("bot must only be of type 'Bot'")
            else:
                self.context = ApplicationContext(bot, interaction)
                self.interaction = self.context.interaction
                self.bot = self.context.bot
                self.command = self.context.command
                self.cog = self.context.cog
                self.user = self.interaction.user

    @classmethod
    def from_context(cls, context: ApplicationContext):
        return cls(context=context)

    @classmethod
    def from_interaction(cls, interaction: Interaction, bot: Bot):
        return cls(interaction=interaction, bot=bot)

    @property
    def response(self):
        return self.interaction.response

    @property
    def guild(self):
        return self.interaction.guild

    @property
    def nsfw(self) -> bool:
        """Returns
               ------
               \rtype[`VoiceChannel`] -> `False`\n
               \rtype[`StageChannel`] -> `False`\n
               \rtype[`PartialMessageable`] -> `True`\n
               \rtype[`Thread`] -> `bool`\n
               \rtype[`TextChannel`] -> ``bool`\n
               \rtype[`CategoryChannel`] -> `bool`\n
               \rtype[`StoreChannel`] -> `bool`
            """
        if isinstance(self.channel, VoiceChannel):
            return False
        elif isinstance(self.channel, StageChannel):
            return False
        elif isinstance(self.channel, Thread):
            return self.channel.is_nsfw()
        elif isinstance(self.channel, TextChannel):
            return self.channel.is_nsfw()
        elif isinstance(self.channel, PartialMessageable):
            return True
        elif isinstance(self.channel, CategoryChannel):
            return self.channel.is_nsfw()

    @property
    def channel(self) -> InteractionChannel:
        return self.interaction.channel

    @property
    def edit_channel(self):
        return self.channel.edit

    @property
    def edit_guild(self):
        return self.guild.edit

    @property
    def send(self):
        """This is the same as `ContextHelper.channel.send`"""
        return self.channel.send

    @property
    def history(self):
        """This is the same as `ContextHelper.channel.history`"""
        return self.channel.history

    @property
    def purge(self):
        """This is the same as `ContextHelper.channel.purge`"""
        return self.channel.purge

    @property
    def defer(self):
        """This is the same as `ContextHelper.interaction.response.defer`"""
        return self.interaction.response.defer

    @property
    def respond(self):
        if not self.interaction.response.is_done():
            return self.interaction.response.send_message
        else:
            return self.interaction.followup.send

    @property
    def send_modal(self):
        """This is the same as `.interaction.response.send_modal`"""
        return self.interaction.response.send_modal

    @property
    def message(self):
        return self.interaction.message

    @property
    def me(self):
        return self.guild.me if self.guild else self.bot.user

    @property
    def guild_me(self):
        return self.guild.me

    @property
    def message_id(self):
        return self.interaction.message.id if self.interaction.message else None

    @property
    def channel_id(self):
        return self.channel.id

    @property
    def followup(self):
        return self.interaction.followup

    @property
    def guild_id(self):
        return self.guild.id if self.guild else None

    @property
    def guild_owner(self):
        return self.guild.owner if self.guild else None

    @property
    def send_response(self):
        if self.response.is_done():
            raise Exception(
                f"Interaction has already been responded to. Use {type(self).__name__}.send_followup instead")
        else:
            return self.response.send_message

    @property
    def send_followup(self):
        if not self.response.is_done():
            raise Exception(
                f"Interaction has not been responded to. Respond with {type(self).__name__}.send_response")
        else:
            return self.followup.send

    @property
    def original_message(self):
        return asyncio.run(self.interaction.original_message())

    @property
    def edit_message(self):
        return self.response.edit_message

    @property
    def is_done(self):
        return self.response.is_done

    @property
    def edit_original_message(self):
        return self.interaction.edit_original_message

    @property
    def delete_message(self):
        return self.interaction.delete_original_message

    @property
    def author(self):
        return self.interaction.user

    time_formatter = discord_time_formatter
    create_view = create_view


class TextInputStyles(Enum):
    singleline = discord.InputTextStyle.singleline
    multiline = discord.InputTextStyle.multiline


async def callback(self: ModalLike, interaction: Interaction):
    pass

def create_modal(title: str, custom_id: str | None = None):
    class PartialModal:
        def __init__(self) -> None:
            self.items: list[discord.ui.InputText] = []
            self.title = title
            self.custom_id = custom_id
            self.callback = callback

        def add_item(self, *, style: TextInputStyles = TextInputStyles.singleline, custom_id: str = MISSING, label: str, placeholder: str = None, min_length: int = None, max_length: int = None, required: bool = True, value: str = None, row: int = None):
            """Creates an `InputText` object with the given values and adds it to `PartialModal.items`"""
            self.items.append(discord.ui.InputText(style=style, label=label, custom_id=custom_id, placeholder=placeholder,
                              min_length=min_length, max_length=max_length, required=required, value=value, row=row))
            return self

        def to_modal(self):
            """Creates a `Modal` object with the previosly given values"""
            modal = discord.ui.Modal(
                title=self.title, custom_id=self.custom_id)
            for item in self.items:
                if isinstance(item, discord.ui.InputText):
                    modal.add_item(item)
            modal.__dict__["callback"] = self.callback
            return modal

        def __call__(self):
            return self.to_modal()

        def add_callback(self, func: Awaitable[Callable[[ModalLike, Interaction], Coroutine[Any, Any, None]]] = None):
            if func is None:
                pass
            else:
                self.callback = func

    return PartialModal()
