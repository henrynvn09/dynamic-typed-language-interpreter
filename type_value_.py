from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    FUNC = "func"


# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value=None):
        self.t = type
        self.v = value

    def value(self):
        self.eval_if_lazy()
        return self.v

    def type(self):
        return self.t

    def eval_if_lazy(self):
        if self.t == Type.FUNC:
            result = self.v()
            self.t = result.type()
            self.v = result.value()
        return False


def get_printable(val):
    if val.type() == Type.NIL:
        return "nil"
    if val.type() == Type.INT:
        return str(val.value())
    if val.type() == Type.STRING:
        return val.value()
    if val.type() == Type.BOOL:
        if val.value() is True:
            return "true"
        return "false"
    return None
