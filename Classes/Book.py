from httpx import Client

from .BookHeader import BookHeader


class Book():
    header: BookHeader
    client: Client

    def __init__(self, client: Client = None, url: str = None):
        if client is None:
            self.client = Client()
        else:
            self.client = client
        self.header = BookHeader()
        if url is not None:
            self.GetBookFromUrl(url)

    def GetBookFromUrl(self, url: str):
        self.header.GetBookHeaderFromUrl(url, self.client)
