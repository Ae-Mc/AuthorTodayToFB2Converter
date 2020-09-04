from dataclasses import dataclass
from typing import List


USERNAME = "<username>"


@dataclass
class Pages:
    main = "https://author.today"
    login = "/account/login"
    logoff = "/account/logoff"
    personalAccount = "/account/my-page"
    profile = "/u/{USERNAME}"
    purchased = "/u/{USERNAME}/library/purchased"
    baseReaderUrl = "/reader"


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

    def __str__(self):
        return "{:35} (id: {})".format(self.title, self.chapterId)

    def __repr__(self):
        return "{:35} (id: {})".format(self.title, self.chapterId)


@dataclass
class BookHeader:
    title: str
    author: str
    annotation: str
    tableOfContents: List[ChapterHeader]
    bookId: int

    def GetReaderUrl(self) -> str:
        return Pages.baseReaderUrl + '/' + str(self.bookId)


@dataclass
class Chapter:
    header: ChapterHeader
    paragraphs: List[str]
