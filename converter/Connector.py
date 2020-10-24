from typing import Callable
from httpx import Client, HTTPStatusError
from bs4 import BeautifulSoup
from FB2 import FictionBook2

from .User import User


def SetRequestVerificationHeader(func) -> Callable:
    def wrapper(*args, **kwargs):
        mainPage = args[0].client.get("/")
        mainPage.raise_for_status()
        DOM = BeautifulSoup(mainPage, "html.parser")
        requestVerificationToken = (
            DOM.select_one("form#logoffForm > input").attrs["value"])
        args[0].client.headers["__RequestVerificationToken"] = (
            requestVerificationToken)
    return wrapper


class Connector:
    client: Client
    user: User

    def __init__(self):
        self.client = Client(base_url="https://author.today", timeout=5)
        self.SetClientHeaders()

    @SetRequestVerificationHeader
    def Login(self, email: str, password: str) -> None:
        data = {"Login": email, "Password": password}
        loginResponse = self.client.post("/account/login", data=data)
        loginResponse.raise_for_status()
        self.LoadUser()

    @SetRequestVerificationHeader
    def Logout(self) -> None:
        logoffResponse = self.client.post(
            "https://author.today/account/logoff", allow_redirects=False)
        if logoffResponse.status_code != 302:
            raise HTTPStatusError(
                message=("Can't logoff!"
                         f" Error code: {logoffResponse.status_code}"),
                request=logoffResponse.request,
                response=logoffResponse)

    def Authorized(self) -> bool:
        pass

    def GetBookById(self, id: int) -> FictionBook2:
        pass

    def GetBookByUrl(self, url: str) -> FictionBook2:
        pass

    def SetClientHeaders(self):
        self.client.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.83 Safari/537.36")
        self.client.headers["dnt"] = '1'
        self.client.headers["cache"] = "no-cache"
        self.client.headers["pragma"] = "no-cache"
        self.client.headers["Upgrade-Insecure-Requests"] = "1"
        self.client.headers["Sec-Fetch-Dest"] = "document"
        self.client.headers["Sec-Fetch-Mode"] = "navigate"
        self.client.headers["Sec-Fetch-Site"] = "same-origin"
        self.client.headers["Sec-Fetch-User"] = "?0"

    def LoadUser(self) -> User:
        pass
