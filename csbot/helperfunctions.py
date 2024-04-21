import os
import math
import pickle
import discord
import constants
import csgo


class DiscordString(str):
    def __new__(self, value):
        obj = str.__new__(self, value)
        return obj

    def __add__(self, __s: str) -> str:
        return DiscordString(super().__add__(__s))

    def to_code_block(self, format_type="ml"):
        return f"```{format_type}\n{self.__str__()}```\n"

    def to_code_inline(self):
        return f"`{self.__str__()}`"


async def do_nothing(*args, **kwargs):
    return


def disable(func):
    return do_nothing


def hide(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    inner.hidden = True
    return inner


def is_hidden(func):
    return getattr(func, "hidden", False)


def infinite_sequence_gen():
    num = 0
    while True:
        yield num
        num += 1


def euclidean_distance(val1, val2):
    return math.sqrt((val1 - val2) ** 2)


def list_ranks() -> DiscordString:
    ranks = ""
    for rank, title in constants.ranks.items():
        ranks += f"{rank}:  {title}\n"
    return DiscordString(ranks)


def get_active_duty() -> list:
    return csgo.get_active_duty()


def list_active_duty() -> DiscordString:
    reply = "Active duty maps: | "
    for map in csgo.get_active_duty():
        reply += f"{map} |"
    reply += "\n"
    return DiscordString(reply)


def log_message(function):
    async def inner(self, message):
        if isinstance(message, discord.RawReactionActionEvent):
            self.log.info(f"{message.user_id} calling: {function.__name__}")
        elif isinstance(message, discord.Message):
            self.log.info(f"{message.author} calling: {function.__name__}")
            self.log.debug(f"Message content: {message.content}")
        await function(self, message)
        self.log.debug("OK")

    return inner


def persist_state(function):
    async def persist_state(self, *args, **kwargs):
        await function(self, *args, **kwargs)
        with open("/home/.csbot/state", "wb") as f:
            pickle.dump(self.players, f)

    return persist_state


def load_state(function):
    def load_state(self, *args, **kwargs):
        function(self, *args, **kwargs)
        try:
            with open("/home/.csbot/state", "rb") as f:
                self.players = pickle.load(f)
        except FileNotFoundError:
            self.players = {}

    return load_state
