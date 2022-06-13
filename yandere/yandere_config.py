"""Config file for the `Yandere` class"""


from dataclasses import dataclass
from enum import Enum


class YandereConfig:

    "A namespace for the config objects"

    class FileUrl:
        def __init__(self, url: str):
            import requests
            self.url = url
            self.code = requests.get(url).content

        def save_to_file(self, file_name: str, file_ext: str):
            with open(f"{file_name}.{file_ext}", "wb") as f:
                f.write(self.code)

        def __str__(self) -> str:
            return self.url

    class YanderePost:
        def __init__(self, post: dict):
            self.post = post
            self.rating: str = post['rating']
            self.id: int = post['id']
            self.file_url: str = post['file_url']
            self.md5: str = post['md5']
            self.source: str | None = post['source'] if post['source'] != '' else None
            self.score: str = post['score']
            self.tags: list[str] = post['tags'].split(' ')
            self.author: str = post['author']
            self.post_url = f"https://yande.re/post/show/{post['id']}"
            self.created_at: int = post['created_at']
            self.updated_at: int = post['updated_at']
            self.creator_id: int = post['creator_id']
            self.status: str = post['status']
            self.jpg_file_url: str = post['jpeg_url']
            self.sample_url: str = post['sample_url']
            self.file_ext: str = post['file_ext']
            self.preview_url: str = post['preview_url']

        def save_photo(self):
            YandereConfig.FileUrl(self.file_url).save_to_file(
                self.md5, self.file_ext)
            print(f"{self.post_url} was saved as {self.md5}.{self.file_ext}")
            import sys, pathlib
            return pathlib.Path(f"{sys.path[0]}\\{self.md5}.{self.file_ext}")

        def __repr__(self) -> str:
            return f"<YanderePost object url='{self.post_url}' id={self.id} md5='{self.md5}'>"

    class ForbiddenTagError(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    class MaxValueException(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    MAX_LIMIT = 10000

