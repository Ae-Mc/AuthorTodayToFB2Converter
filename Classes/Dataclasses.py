from dataclasses import dataclass
from typing import List


USERNAME = "<username>"


@dataclass
class Pages:
    main = "https://author.today"
    login = f"{main}/account/login"
    personalAccount = f"{main}/account/my-page"
    profile = f"{main}/u/{USERNAME}"
    purchased = f"{main}/u/{USERNAME}/library/purchased"
    baseReaderUrl = f"{main}/reader"


@dataclass
class User:
    username: str = ""
    email: str = ""
    userId: int = 0


@dataclass
class ChapterHeader:
    title: str
    chapterId: int
    length: int


@dataclass
class BookHeader:
    title: str
    author: str
    tableOfContents: List[ChapterHeader]
    bookId: int

    def GetReaderUrl(self) -> str:
        return Pages.baseReaderUrl + '/' + str(self.bookId)
