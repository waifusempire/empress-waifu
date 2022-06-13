import random
from typing import Any, Iterable, SupportsIndex, Type, TypeVar, overload
from typing_extensions import Self
from praw.models.helpers import SubredditHelper
from praw.reddit import Submission
from config import client_agent_1, client_id_1, client_secret_1
import praw


End = TypeVar("End", bound="List")


class RedditPost:
    def __init__(self, data):
        self._data = data

    @property
    def title(self) -> str:
        return self.original.title

    @property
    def url(self) -> str:
        return self.original.url

    @property
    def upvotes(self) -> int:
        return self.original.ups

    @property
    def downvotes(self) -> int:
        return self.original.downs

    @property
    def downvote(self):
        return self.original.downvote

    @property
    def upvote(self):
        return self.original.upvote

    @property
    def award(self):
        return self.original.award

    @property
    def comment_limit(self):
        return self.original.comment_limit

    @property
    def original(self) -> Submission:
        return self._data

    @property
    def comment_sort(self):
        return self.original.comment_sort

    @property
    def clear_vote(self):
        return self.original.clear_vote

    @property
    def comments(self):
        return self.original.comments

    @property
    def crosspost(self):
        return self.original.crosspost

    @property
    def delete(self):
        return self.original.delete

    @property
    def disable_inbox_replies(self):
        return self.original.disable_inbox_replies

    @property
    def duplicates(self):
        return self.original.duplicates

    @property
    def edit(self):
        def _(body: str):
            return type(self)(self.original.edit(body))
        return _

    @property
    def flair(self):
        return self.original.flair

    @property
    def fullname(self):
        return self.original.fullname

    @property
    def gild(self):
        return self.original.gild

    @property
    def hide(self):
        return self.original.hide

    @property
    def id(self):
        return self.original.id

    @property
    def id_from_url(self):
        return self.original.id_from_url

    @property
    def mark_visited(self):
        return self.original.mark_visited

    @property
    def mod(self):
        return self.original.mod

    @property
    def report(self):
        return self.original.report

    @property
    def reply(self):
        return self.original.reply

    @property
    def parse(self):
        return self.original.parse

    @property
    def save(self):
        return self.original.save

    @property
    def shortlink(self):
        return self.original.shortlink

    @property
    def unsave(self):
        return self.original.unsave

    @property
    def unhide(self):
        return self.original.unhide

    @property
    def over_18(self) -> bool:
        return self.original.over_18


class List(list):

    @classmethod
    def from_args(cls, *args):
        return cls(args)

    @classmethod
    def from_kwargs(cls, **kwargs):
        l = cls()
        for i, j in kwargs.items():
            k = cls()
            k.__init__((i, j))
            l.append(k)
        return l

    @classmethod
    def from_dict(cls, dict_: dict, /):
        return cls.from_kwargs(**dict_)

    @property
    def tuple(self):
        return tuple(self)

    def append(self, __object: object | None, /) -> Self:
        super().append(__object)
        return self

    def insert(self, __index: SupportsIndex, __object: object | None) -> Self:
        super().insert(__index, __object)
        return self

    @overload
    def add(self: Self, __object: object | None, /) -> Self:
        "Append object to the end of the list."
        ...

    @overload
    def add(self: Self, __object: object | None, /, __index: int) -> Self:
        "Insert object before index."
        ...

    def add(self: Self, __object: object | None, /, __index: int = End) -> Self:
        if __index == End:
            self.append(__object)
        else:
            self.insert(__index, __object)
        return self

    def add_args(self: Self, *args, index: int = ...):
        if not index == ...:
            for num, obj in enumerate(args):
                self.add(obj, index + num)
        else:
            for obj in args:
                self.add(obj)
        return self

    def add_start(self, *__objects: object | None):
        """Add objects to the start of the list."""
        return self.add_args(*__objects, index=0)


REDDIT = praw.Reddit(
    client_id=client_id_1, client_secret=client_secret_1, user_agent=client_agent_1, check_for_async=False)
SUBREDDIT = REDDIT.subreddit


class RedditClass:
    def __init__(self, _data: list[RedditPost]):
        self._len = len(_data)
        self._place = -1
        self._data: Any = _data

    def __iter__(self):
        return self

    def __next__(self) -> RedditPost:
        if self._place >= self._len:
            raise StopIteration("Out of range")
        else:
            self._place += 1
            return self._data[self._place]

    @property
    def posts(self) -> list[RedditPost]:
        return self._data

    def __call__(self):
        "Calls the `next` method on the iterator"
        return self.__next__()

    @property
    def random_post(self):
        "Returns a random `Submission` object"
        return random.choice(self.posts)


def get_reddit_posts(subreddit: SubredditHelper):
    sub_sub = SUBREDDIT(subreddit).hot()
    return RedditClass([RedditPost(x) for x in sub_sub if not x.stickied])
