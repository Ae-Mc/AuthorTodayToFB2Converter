import re
from dataclasses import dataclass
from os import mkdir, path
from json import loads
from typing import List

from bs4 import BeautifulSoup
from requests import Response, Session

OutputFolder = "Output"
try:
    mkdir(OutputFolder)
except FileExistsError:
    pass

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


def GetBookChapters(url: str, session: Session) -> List[Chapter]:
    with session.get(url) as readerResponse:
        responseText = readerResponse.text
        searchResult = re.search(
            r"app.init\(\"readerIndex\", \{.*chapters: "
            r"(\[.*\])"
            r",[ \n\r]*chapterProgress",
            responseText,
            re.DOTALL)
        chapters: List[Chapter] = []
        if searchResult is not None and readerResponse.status_code == 200:
            rawChapters = loads(searchResult.group(1))
            for rawChapter in rawChapters:
                chapters.append(Chapter(rawChapter["title"],
                                        rawChapter["id"],
                                        rawChapter["textLength"]))
        else:
            print("Error! Can't get chapters from url {url}!")
        return chapters


def GetRequestVerificationToken(response: Response) -> str:
    DOM: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    return DOM.select_one("form#logoffForm > input").attrs["value"]


def SearchGroupOne(pattern: str, text: str) -> str:
    expr = re.compile(pattern)
    searchResult = expr.search(text)
    if searchResult is not None:
        return searchResult.group(1)
    else:
        return ""


def GetUser(session: Session) -> User:
    with session.get(Pages.personalAccount) as personalAccountResponse:
        responseText = personalAccountResponse.text
        user = User()
        user.username = SearchGroupOne(
            r"ChatraIntegration.name = ['\"](.*)['\"]", responseText)
        user.email = SearchGroupOne(
            r"ChatraIntegration.email = ['\"](.*)['\"]", responseText)
        searchResult = SearchGroupOne(
            r"ga\('set', 'userId', '(\d*)'\)", responseText)
        user.userId = 0 if len(searchResult) == 0 else int(searchResult)
        return user


def Authorize(session: Session) -> bool:
    with open("./PrivateConfig/mainPassword.txt") as f:
        password = f.readlines()[0]
    with open("./PrivateConfig/mail.ru-email.txt") as f:
        email = f.readlines()[0]
    data = {
        "Login": email,
        "Password": password
    }
    requestVerificationToken = GetRequestVerificationToken(
        session.get(Pages.login))
    session.headers["__RequestVerificationToken"] = requestVerificationToken
    with session.post(Pages.login, data) as loginResponse:
        if loginResponse.status_code != 200:
            print(
                "Error! Can't log in! Error code: {loginResponse.status_code}")
            return False
    return True


with Session() as session:
    if Authorize(session):
        user = GetUser(session)
        print(f"\n[LOG] Successful log in as {user.username} aka {user.email} "
              f"(id: {user.userId})!")
        with session.get(Pages.purchased) as purchasedResponse:
            DOM: BeautifulSoup = BeautifulSoup(purchasedResponse.text,
                                               "html.parser")
            bookShelf = DOM.select_one("div.book-shelf")
            for book in bookShelf.find_all("div", attrs={"class": "bookcard"}):
                author = book.find(
                    "h5", attrs={"class": "bookcard-authors"}).a.text
                title = book.find(
                    "h4", attrs={"class": "bookcard-title"}).a.text
                url = Pages.main + book.find("div", attrs={
                    "class": "thumb-buttons"}).find_all("a")[1]["href"]
                print(f"\n{author}. «{title}» ({url})")
                chapters = GetBookChapters(url, session)
                print(*chapters, sep="\n")
