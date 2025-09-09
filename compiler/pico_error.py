from tokenizer import Token


class PicoError(Exception):
    def __init__(self, msg: str, token: Token):
        self.msg = msg
        self.origin = token
        super().__init__(self.msg)


class PicoSyntaxError(PicoError):
    def __init__(self, msg: str, token: Token):
        super().__init__(msg,token)
