import re

from bs4 import BeautifulSoup
from httpx import Client, Response

from .Dataclasses import Pages, User


def SetSessionHeaders(client: Client):
    client.headers
    client.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.83 Safari/537.36")
    client.headers["dnt"] = '1'
    client.headers["cache"] = "no-cache"
    client.headers["pragma"] = "no-cache"
    client.headers["Upgrade-Insecure-Requests"] = "1"
    client.headers["Sec-Fetch-Dest"] = "document"
    client.headers["Sec-Fetch-Mode"] = "navigate"
    client.headers["Sec-Fetch-Site"] = "same-origin"
    client.headers["Sec-Fetch-User"] = "?0"


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


def GetUser(client: Client) -> User:
    personalAccountResponse = client.get(Pages.personalAccount)
    personalAccountResponse.raise_for_status()
    responseText = personalAccountResponse.text
    user = User()
    user.username = SearchGroupOne(
        r"ChatraIntegration.name = ['\"](.*)['\"]", responseText)
    user.email = SearchGroupOne(
        r"ChatraIntegration.email = ['\"](.*)['\"]", responseText)
    searchResult = SearchGroupOne(
        r"ga\('set', 'userId', '(\d*)'\)", responseText)
    user.userId = int(searchResult) if len(searchResult) else -1
    return user


def Authorize(client: Client) -> bool:
    with open("./PrivateConfig/mainPassword.txt") as f:
        password = f.readlines()[0]
    with open("./PrivateConfig/mail.ru-email.txt") as f:
        email = f.readlines()[0]
    data = {
        "Login": email,
        "Password": password
    }
    loginPage = client.get(Pages.login)
    loginPage.raise_for_status()
    requestVerificationToken = GetRequestVerificationToken(loginPage)
    client.headers["__RequestVerificationToken"] = requestVerificationToken
    loginResponse = client.post(Pages.login, data=data)
    loginResponse.raise_for_status()
    del client.headers["__RequestVerificationToken"]
    return True


def Logoff(client: Client) -> bool:
    mainPage = client.get(Pages.main)
    mainPage.raise_for_status()
    requestVerificationToken = GetRequestVerificationToken(mainPage)
    client.headers["__RequestVerificationToken"] = requestVerificationToken
    logoffResponse = client.post(Pages.logoff, allow_redirects=False)
    if logoffResponse.status_code != 302:
        print("Error! Can't log off!"
              f" Error code: {logoffResponse.status_code}")
        return False
    return True
