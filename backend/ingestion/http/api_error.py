class ApiError(Exception):
    """Une API a refusé ou échoué même après toutes les reprises."""

    def __init__(self, source: str, url: str, reason: str) -> None:
        super().__init__(f"{source} : {url} a échoué ({reason})")
        self.source = source
        self.url = url
        self.reason = reason
