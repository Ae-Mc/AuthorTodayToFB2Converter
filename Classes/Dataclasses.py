from dataclasses import dataclass


USERNAME = "<username>"


@dataclass
class Pages:
    main = "https://author.today"
    login = f"{main}/account/login"
    personalAccount = f"{main}/account/my-page"
    profile = f"{main}/u/{USERNAME}"
    purchased = f"{main}/u/{USERNAME}/library/purchased"


@dataclass
class User:
    username: str = ""
    email: str = ""
    userId: int = 0


@dataclass
class Chapter:
    title: str
    chapterId: int
    length: int
