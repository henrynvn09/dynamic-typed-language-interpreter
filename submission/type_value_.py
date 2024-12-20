from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"


# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value=None):
        self.t = type
        self.v = value

    def value(self):
        return self.v

    def type(self):
        return self.t


def get_printable(val):
    if not val:
        return ""
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

    # for structs case of NIL
    if not is_generic_type(val.type()) and val.value() == None:
        return "nil"

    # we don't have to handle struct not NIL
    return None


def is_generic_type(val_type):
    return val_type and val_type in vars(Type).values()


def is_non_nil_generic_type(val_type):
    return val_type in [Type.INT, Type.STRING, Type.BOOL]
