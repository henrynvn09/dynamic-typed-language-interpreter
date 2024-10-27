from element import Element
from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

UNDEFINED_VALUE = "_undefined_"


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)  # call InterpreterBase's constructor
        self.variables = dict()

    def run(self, program: Element):
        parsed_program = parse_program(program)

        program_functions = parsed_program.get("functions")

        main_functions = [x for x in program_functions if x.get("name") == "main"]

        if not main_functions:
            super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
        main_function = main_functions[0]

        for statement in main_function.get("statements"):
            self.interpret_statement(statement)

    def is_variable_defined(self, var_name):
        return var_name in self.variables

    def interpret_statement(self, statement: Element):
        if statement.elem_type == "vardef":
            var_name = statement.get("name")
            if self.is_variable_defined(var_name):
                super().error(
                    ErrorType.NAME_ERROR,
                    f"Variable {var_name} defined more than once",
                )
            self.variables[statement.get("name")] = UNDEFINED_VALUE

        elif statement.elem_type == "=":
            var_name = statement.get("name")
            if not self.is_variable_defined(var_name):
                super().error(
                    ErrorType.NAME_ERROR,
                    f"Variable {var_name} has not been defined",
                )

            self.variables[var_name] = self.get_node_value(statement.get("expression"))

        elif statement.elem_type == "fcall":
            self.handle_function_call(statement)
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Unknown statement type {statement.get('type')}",
            )

    def interpret_expression(self, expression: Element):
        if expression.elem_type in ["+", "-"]:
            operand = expression.elem_type
            op1 = self.get_node_value(expression.get("op1"))
            op2 = self.get_node_value(expression.get("op2"))
            return self.evaluate_operand(operand, op1, op2)

        if expression.elem_type == "fcall":
            return self.handle_function_call(expression)

        super().error(
            ErrorType.TYPE_ERROR,
            f"Unknown expression type {expression.elem_type}",
        )

    def get_node_value(self, node):
        if node.elem_type == "var":
            return self.get_variable_value(node.get("name"))
        if node.elem_type == "int":
            return node.get("val")
        if node.elem_type == "string":
            return node.get("val")
        # otherwise, it's an expression
        return self.interpret_expression(node)

    def get_variable_value(self, var_name):
        if not self.is_variable_defined(var_name):
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )

        return self.variables[var_name]

    def evaluate_operand(self, operand: str, op1, op2):
        if type(op1) != type(op2):
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for arithmetic operation",
            )

        if operand == "+":
            return op1 + op2
        elif operand == "-":
            return op1 - op2
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Unknown operand {operand}",
            )

    def handle_function_call(self, function: Element):
        function_name = function.get("name")

        if function_name == "print":
            # Your print function call must accept zero or more arguments,
            # which it will evaluate to get a resulting value, then concatenate
            # without spaces into a string, and then output using the output()
            # method in our InterpreterBase base class:
            output = ""
            for arg in function.get("args"):
                output += str(self.get_node_value(arg))
            super().output(output)

        elif function_name == "inputi":
            if len(function.get("args")) > 1:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"No inputi() function found that takes > 1 parameter",
                )

            if len(function.get("args")) == 1:
                prompt = function.get("args")[0]
                super().output(prompt.get("val"))
            user_inputstring = super().get_input()
            user_input = int(user_inputstring)

            return user_input

        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {function_name} has not been defined",
            )
