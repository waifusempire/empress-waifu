from typing import Type, overload, final
from typing_extensions import Self
from yandere.yandere_config import YandereConfig


YanderePost = YandereConfig.YanderePost


@final
class Yandere:

    @overload
    def __init__(self: Self,
    *tags: str | None,
    limit: int = ...,
    explicit: bool = ...,
    forbidden_tags: list[str] | None = ...
    ) -> None: ...

    @overload
    def __init__(self: Self,
    tags: list[str] | None = ..., /, *,
    limit: int = ...,
    explicit: bool = ...,
    forbidden_tags: list[str] | None = ...
    ) -> None: ...

    @property
    def random_post(self: Self) -> YanderePost: ...

    def flatten(self: Self) -> list[YanderePost]: ...

    def __iter__(self: Self) -> Self: ...

    def __next__(self: Self) -> YanderePost: ...

    def __str__(self: Self) -> str: ...

    def __len__(self: Self) -> int: ...

    def to_dict(self: Self
    ) -> dict[str, str | list[str] | int | list[dict] | None]: ...

    @overload
    @classmethod
    def new(cls: Type[Self],
    *tags: str | None,
    limit: int = ...,
    explicit: bool = ...,
    forbidden_tags: list[str] | None = ...
    ) -> Yandere: ...

    @overload
    @classmethod
    def new(cls: Type[Self],
    tags: list[str] | None = ..., /, *,
    limit: int = ...,
    explicit: bool = ...,
    forbidden_tags: list[str] | None = ...
    ) -> Yandere: ...

    def __enter__(self: Self) -> Self: ...

    def __exit__(self: Self, *args) -> None: ...

    def copy(self: Self) -> Yandere: ...