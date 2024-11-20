class UserException(Exception):
    "Raised when user use raise their own exception"

    DIVBYZERO = "div0"

    def __init__(self, exception_type):
        self.exception_type = exception_type
