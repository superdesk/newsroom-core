class AuthorizationError(Exception):
    code: int
    message: str
    title: str | None

    def __init__(self, code: int, message: str, title: str | None = None):
        super().__init__(self)
        self.code = code
        self.message = message
        self.title = title
