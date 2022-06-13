"""Yandere class"""


from typing import Type, overload, final
from typing_extensions import Self


@final
class Yandere:

    """Parameters
    ----------
    tags: `str` or `list[str]` - default `None`\n
    limit: `int` - default `100` - The max limit is `10000`\n
    explicit: `bool` - default `False`\n
    forbidden_tags: `list[str]` - If `None` it takes the default list\n
    Attributes
    ----------\n
    forbidden_tags: `list[str]`\n
    original_posts: `list[dict]`\n
    posts: `list[YanderePost]`\n
    Raises
    ------\n
    ForbiddenTagError - 
    On banned tags!\n
    MaxValueException - 
    If the limit is set higher than `10000`\n
    And other exceptions that may rise during the http request\n
    Exception - if subclassed"""

    @overload
    def __init__(self, *tags: str | None, limit: int = ..., explicit: bool = ..., forbidden_tags: list[str] | None = ...):
        ...

    @overload
    def __init__(self, tags: list[str] | None = ..., /, *, limit: int = ..., explicit: bool = ..., forbidden_tags: list[str] | None = ...):
        ...

    def __init__(self, *tags: str | None, limit: int = 100, explicit: bool = False, forbidden_tags: list[str] | None = None):
        self._forbidden_tags: list[str] = forbidden_tags if forbidden_tags != None else [
            "loli", "shota"]

        if len(tags) == 0:
            self._t = None
        elif isinstance(tags[0], list):
            if tags[0] == [None]:
                self._t = None
            else:
                self._t = [i for i in tags[0] if isinstance(i, str)]
        else:
            a: list[str] = []
            for i in tags:
                if isinstance(i, str):
                    a.append(i)
            self._t = a

        self._tags = "+".join(self._t) if len(tags) != 0 else None

        if limit == 0:
            self._limit = 1
        elif limit < 0:
            self._limit = 1
        else:
            self._limit = limit
        self._explicit = explicit

        self._i: int = -1

        from .yandere_config import YandereConfig
        import requests

        POST = YandereConfig.YanderePost
        FORBIDDEN_TAG_ERROR = YandereConfig.ForbiddenTagError
        MAX_VALUE_EXCEPTION = YandereConfig.MaxValueException
        MAX_LIMIT = YandereConfig.MAX_LIMIT

        if not self._t == None:
            if len(self._t) != 0:
                for tag in self._t:
                    if any(word in tag.lower() for word in self._forbidden_tags):
                        raise FORBIDDEN_TAG_ERROR(
                            f"'{tag}' is a forbidden tag!")
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass

        if self._limit > MAX_LIMIT:
            raise MAX_VALUE_EXCEPTION(
                f"Limit '{limit}' is above the maximum allowed number '10000'")

        if not explicit:
            if not self._t == None:
                url = f"https://yande.re/post.json/?limit={self._limit}&tags=-loli+-shota+-cub+{self._tags}"
                self._u = url
                responses = requests.get(url).json()
                self.original_posts: list[dict] = responses
                posts: list[POST] = []
                for item in responses:
                    posts.append(POST(item))
                self.posts = posts
                return
            else:
                url = f"https://yande.re/post.json/?limit={self._limit}&tags=-loli+-shota+-cub"
                self._u = url
                responses = requests.get(url).json()
                self.original_posts: list[dict] = responses
                posts: list[POST] = []
                for item in responses:
                    posts.append(POST(item))
                self.posts = posts
                return
        else:
            if not self._t == None:
                url = f"https://yande.re/post.json/?limit={self._limit}&tags=rating:explicit+-loli+-shota+-cub+{self._tags}"
                self._u = url
                responses = requests.get(url).json()
                self.original_posts: list[dict] = responses
                posts: list[POST] = []
                for item in responses:
                    posts.append(POST(item))
                self.posts = posts
                return
            else:
                url = f"https://yande.re/post.json/?limit={self._limit}&tags=rating:explicit+-loli+-shota+-cub"
                self._u = url
                responses = requests.get(url).json()
                self.original_posts: list[dict] = responses
                posts: list[POST] = []
                for item in responses:
                    posts.append(POST(item))
                self.posts = posts
                return

    @property
    def random_post(self):
        '''Gives a random post from the collection'''
        import random
        return random.choice(self.posts)

    def flatten(self):
        return self.posts

    def __iter__(self):
        return self

    def __next__(self):
        """Example
        =======
        >>> yandere = Yandere()
        >>> post = yandere.__next__()
        >>> post.file_url
        'https://files.yande.re/sample/5e5edecb98d2fb9b459e8117681701c5/yande.re%20923586%20sample%20horns%20kobayashi-san_chi_no_maid_dragon%20maid%20mossi%20tooru_%28kobayashi-san_chi_no_maid_dragon%29.jpg'
        """
        if self._i >= len(self.posts)-1:
            raise StopIteration("Iterator out of range")
        else:
            self._i += 1
            return self.posts[self._i]

    def __str__(self):
        return f"<{type(self).__name__} object posts: {self.__len__()}>"

    def __len__(self):
        return len(self.posts)

    def to_dict(self):
        return dict(url=self._u, tags=self._t, forbidden_tags=self._forbidden_tags, limit=self._limit, posts=self.original_posts, explicit=self._explicit)

    @overload
    @classmethod
    def new(cls: Type[Self], *tags: str | None, limit: int = ..., explicit: bool = ..., forbidden_tags: list[str] | None = ...) -> Self:
        ...

    @overload
    @classmethod
    def new(cls: Type[Self], tags: list[str] | None = ..., /, *, limit: int = ..., explicit: bool = ..., forbidden_tags: list[str] | None = ...) -> Self:
        ...

    @classmethod
    def new(cls: Type[Self], *tags: str | list[str] | None, limit: int = 100, explicit: bool = False, forbidden_tags: list[str] | None = None) -> Self:
        return cls(*tags, limit=limit, explicit=explicit, forbidden_tags=forbidden_tags)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.posts = []
        self.original_posts = []
        self._i = -1
        self._forbidden_tags = []
        self._t = None
        self._explicit = False
        self._limit = 100
        self._u = None
        self._tags = None
        return

    def __init_subclass__(cls) -> None:
        raise Exception(
            f"Base class \"Yandere\" is marked final and cannot be subclassed")

    def __copy__(self):
        copy = type(self).__new__(type(self))
        copy.posts = self.posts.copy()
        copy.original_posts = self.original_posts.copy()
        copy._explicit = self._explicit
        copy._i = self._i
        copy._forbidden_tags = self._forbidden_tags.copy()
        copy._limit = self._limit
        copy._tags = self._tags
        copy._t = self._t.copy() if self._t else None
        copy._u = self._u
        return copy

    def copy(self):
        return self.__copy__()
