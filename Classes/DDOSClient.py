import httpx


class Client(httpx.Client):

    def get(self, *args, **kwargs) -> httpx.Response:
        try:
            return super().get(*args, **kwargs)
        except httpx.ReadTimeout:
            print("Error! Read operation timed out! Restarting...")
            return self.get(*args, **kwargs)

    def post(self, *args, **kwargs) -> httpx.Response:
        try:
            return super().post(*args, **kwargs)
        except httpx.ReadTimeout:
            print("Error! Read operation timed out! Restarting...")
            return self.post(*args, **kwargs)
