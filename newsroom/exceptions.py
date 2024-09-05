import json
from typing import Any
from werkzeug.exceptions import HTTPException


class AuthorizationError(Exception):
    code: int
    message: str

    def __init__(self, code: int, message: str):
        super().__init__(self)
        self.code = code
        self.message = message


class ValidationException(HTTPException):
    """
    Custom exception class to handle validation errors and return them in a JSON format.

    This exception is intended to be raised when there are validation errors in user input
    during request processing.

    Attributes:
        code (int): HTTP status code, defaults to 400 (Bad Request).
        errors (Any): A collection of validation error details that will be returned in the response.
    """

    code = 400

    def __init__(self, errors: Any, description=None):
        super().__init__(description)
        self.errors = errors

    def get_body(self, *args):
        return json.dumps(self.errors)

    def get_headers(self, *args):
        """Ensure that the content type is JSON"""
        return [("Content-Type", "application/json")]
