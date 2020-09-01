from dataclasses import dataclass
from os import mkdir, path

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


def GetBookFirstChapter(url: str, session: Session):
    with session.get(url) as reader:
        print(reader.url)


def GetRequestVerificationToken(response: Response) -> str:
    DOM: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    return DOM.select_one("form#logoffForm > input").attrs["value"]


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
                print(f"{author}. «{title}» ({url})")
                GetBookFirstChapter(url, session)

            with open(path.join(OutputFolder,
                                "purchased.php"),
                      "w") as purchasedFile:
                purchasedFile.write(purchasedResponse.text)
