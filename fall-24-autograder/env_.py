# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
from type_value_ import Type, Value, is_generic_type


class EnvironmentManager:
    def __init__(self):
        self.environment = {}

    # Gets the data associated a variable name
    def get(self, symbol):
        if symbol in self.environment:
            return self.environment[symbol]
        return None

    # Sets the data associated with a variable name
    def set(self, symbol, value: Value):
        if symbol not in self.environment:
            raise Exception("Variable not found in environment")

        # if the current type is a generic type and the new value is not the same type, raise an error
        if (
            is_generic_type(self.environment[symbol].type())
            and self.environment[symbol].type() != value.type()
        ):
            raise TypeError(
                f"Cannot assign {value.type()} to {self.environment[symbol].type()}"
            )

        # if the current type is a struct and the new value other than NIL or struct, raise an error
        if (
            not is_generic_type(self.environment[symbol].type())
            and value.type() != Type.NIL
            and value.type() != self.environment[symbol].type()
        ):
            raise TypeError(
                f"Cannot assign non nil value to {self.environment[symbol].type()}"
            )

        self.environment[symbol].v = value.v

    def create(self, symbol, start_val):
        if symbol not in self.environment:
            self.environment[symbol] = start_val
            return True
        return False
