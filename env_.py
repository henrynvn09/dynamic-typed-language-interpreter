# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.environment = {}

    # Gets the data associated a variable name
    def get(self, symbol):
        if symbol in self.environment:
            return self.environment[symbol]
        return None

    # Sets the data associated with a variable name
    def set(self, symbol, value):
        if symbol not in self.environment:
            return False
        self.environment[symbol] = value
        return True

    def create(self, symbol, start_val):
        if symbol not in self.environment:
            self.environment[symbol] = start_val
            return True
        return False


class ScopeType:
    FUNCTION = "function"
    BLOCK = "block"


class EnvironmentStackManager:
    def __init__(self):
        self.variable_scope_stack = []  # stack of function call
        self.top = None  # EnvironmentManager of the current function scope

    def create_new_function_scope(self, args, values, arg_def):
        """Initialize new variable scope for a function"""
        self.variable_scope_stack.append((ScopeType.FUNCTION, EnvironmentManager()))
        # current environment is top of stack
        self.top = self.variable_scope_stack[-1][1]
        for arg, value in zip(args, values):
            arg_def(arg.get("name"), value)

    def create_new_block_scope(self):
        """Initialize new variable scope for a block"""
        self.variable_scope_stack.append((ScopeType.BLOCK, EnvironmentManager()))
        self.top = self.variable_scope_stack[-1][1]

    def destroy_top_scope(self):
        """Destroy the current function scope, doesn't check errors"""
        self.variable_scope_stack.pop()
        self.top = (
            self.variable_scope_stack[-1][1] if self.variable_scope_stack else None
        )

    def __iter__(self):
        return iter(self.variable_scope_stack)

    def __reversed__(self):
        return reversed(self.variable_scope_stack)
