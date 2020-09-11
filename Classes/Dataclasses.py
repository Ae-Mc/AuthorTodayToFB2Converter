from dataclasses import dataclass


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
    id: int

    def __str__(self):
        return "{:35} (id: {})".format(self.title, self.id)

    def __repr__(self):
        return "{:35} (id: {})".format(self.title, self.id)


@dataclass
class Sequence:
    name: str
    number: int
