from httpx import AsyncClient
from FB2 import FictionBook2

from .User import User


class Connector:
    client: AsyncClient
    user: User

    def __init__(self):
        self.client = AsyncClient(base_url="https://author.today", timeout=5)
        self.SetClientHeaders()

    async def Login(self, email: str, password: str) -> None:
        pass

    async def Logout(self) -> None:
        pass

    async def Authorized(self) -> bool:
        pass

    async def GetBookById(self, id: int) -> FictionBook2:
        pass

    async def GetBookByUrl(self, url: str) -> FictionBook2:
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
