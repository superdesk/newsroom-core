class AuthorizationError(Exception):
    code: int
    message: str

    def __init__(self, code: int, message: str):
        super().__init__(self)
        self.code = code
        self.message = message
