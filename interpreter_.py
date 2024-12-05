# Add to spec:
# - printing out a nil value is undefined

from env_ import EnvironmentStackManager, ScopeType
from type_value_ import Type, Value, get_printable
from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from element import Element
from user_exception_ import UserException


# Main interpreter class
class Interpreter(InterpreterBase):
    # constants
    UNARY_OPS = {"!", "neg"}
    BIN_OPS_EXCEPT = {"==", "!="}
    BIN_OPS = {"+", "-", "*", "/", ">=", "<=", ">", "<", "==", "!=", "||", "&&"}

    # methods
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.__setup_ops()
        self.func_name_to_ast = {}  # dict of function names to its node
        self.env_scope_stack = EnvironmentStackManager()  # stack of function call

    # run a program that's provided in a string
    # usese the provided Parser found in brewparse.py to parse the program
    # into an abstract syntax tree (ast)
    def run(self, program):
        ast = parse_program(program)
        self.__set_up_function_table(ast)
        try:
            self.__run_function("main", lazy=False)
        except UserException:
            super().error(ErrorType.FAULT_ERROR, "Uncaught exception")

    def __run_function(self, func_name, passed_arguments=[], lazy=True):
        """run a function based on name and list of arguments, if lazy argument is evaluated lazily and return lazy value"""
        # TODO: double check modifying passed_arguments inside function
        evaluated_args = [self.__eval_expr(arg, True) for arg in passed_arguments]
        func_def: Element = self.__get_func(func_name, passed_arguments)

        def run():
            self.env_scope_stack.create_new_function_scope(
                func_def.get("args"),
                evaluated_args,
                self.__arg_def,
            )
            _, return_val = self.__run_statements(func_def.get("statements"))
            self.env_scope_stack.destroy_top_scope()
            return return_val if return_val is not None else Value(Type.NIL, None)

        return self.__lazify(run, lazy)

    def __set_up_function_table(self, ast):
        """function table is a dictionary of (function name, number of arguments) to the AST node"""
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            self.func_name_to_ast[(func_def.get("name"), len(func_def.get("args")))] = (
                func_def
            )

    def __get_func(self, name, args):
        """get a function by name and number of arguments"""
        n_args = len(args)
        if (name, n_args) not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        return self.func_name_to_ast[(name, n_args)]

    def __run_statements(self, statements):
        "if there is a return statement, return True, value. otherwise return False, None"
        # create a block scope
        self.env_scope_stack.create_new_block_scope()

        for statement in statements:
            if self.trace_output:
                print(statement)
            if statement.elem_type == InterpreterBase.FCALL_NODE:
                # a single function call statement is eagerly evaluated
                self.__call_func(statement, lazy=False)
            elif statement.elem_type == "=":
                self.__assign(statement)
            elif statement.elem_type == InterpreterBase.VAR_DEF_NODE:
                self.__var_def(statement)
            elif statement.elem_type == InterpreterBase.IF_NODE:
                is_return, return_value = self.__do_if(statement)
                if is_return:
                    self.env_scope_stack.destroy_top_scope()
                    return is_return, return_value
            elif statement.elem_type == InterpreterBase.RETURN_NODE:
                self.env_scope_stack.destroy_top_scope()
                return True, self.__return_value(statement)
            elif statement.elem_type == InterpreterBase.FOR_NODE:
                is_return, return_value = self.__do_for(statement)
                if is_return:
                    self.env_scope_stack.destroy_top_scope()
                    return is_return, return_value
            elif statement.elem_type == InterpreterBase.TRY_NODE:
                is_return, return_value = self.__do_try_catch(statement)
                if is_return:
                    self.env_scope_stack.destroy_top_scope()
                    return is_return, return_value
            elif statement.elem_type == InterpreterBase.RAISE_NODE:
                self.__do_raise(statement)

        # destroy block scope
        self.env_scope_stack.destroy_top_scope()
        return False, None

    def __return_value(self, return_ast):
        value = self.__eval_expr(return_ast.get("expression"), lazy=True)
        return value

    # TODO: double check loop logic lazy evaluation
    def __do_for(self, for_ast):
        "Evaluate for loop, condition is evaluated eagerly"
        init = for_ast.get("init")
        condition = for_ast.get("condition")
        update = for_ast.get("update")
        statements = for_ast.get("statements")

        self.env_scope_stack.create_new_block_scope()
        self.__assign(init)

        evaluated_condition = self.__eval_expr(condition, lazy=False)
        while evaluated_condition.value():
            if evaluated_condition.type() != Type.BOOL:
                super().error(
                    ErrorType.TYPE_ERROR, "for condition must be a boolean expression"
                )

            is_return, return_value = self.__run_statements(statements)
            if is_return:
                self.env_scope_stack.destroy_top_scope()  # TODO: destroy until function scope
                return is_return, return_value
            self.__run_statements([update])
            evaluated_condition = self.__eval_expr(condition, lazy=False)
        self.env_scope_stack.destroy_top_scope()
        return False, None

    def __do_if(self, if_ast):
        # condition must be evaluated eagerly
        condition = self.__eval_expr(if_ast.get("condition"), lazy=False)
        if condition.type() != Type.BOOL:
            super().error(
                ErrorType.TYPE_ERROR, "If condition must be a boolean expression"
            )
        statements = if_ast.get("statements")
        else_statements = (
            if_ast.get("else_statements") if if_ast.get("else_statements") else []
        )
        if condition.value():
            is_return, return_value = self.__run_statements(statements)
        else:
            is_return, return_value = self.__run_statements(else_statements)
        return is_return, return_value

    def __do_try_catch(self, try_ast):
        statements = try_ast.get("statements")
        catchers = try_ast.get("catchers")
        exceptions = {c.get("exception_type"): c.get("statements") for c in catchers}

        # Mark the current scope as the start of the try-catch block
        self.env_scope_stack.mark_scope()

        try:
            is_return, return_value = self.__run_statements(statements)
            self.env_scope_stack.unmark_scope()
        except ZeroDivisionError:
            self.env_scope_stack.jump_to_marked_scope()

            if UserException.DIVBYZERO in exceptions:
                is_return, return_value = self.__run_statements(
                    exceptions[UserException.DIVBYZERO]
                )
            else:
                raise ZeroDivisionError
        except UserException as e:
            self.env_scope_stack.jump_to_marked_scope()

            if e.exception_type in exceptions:
                is_return, return_value = self.__run_statements(
                    exceptions[e.exception_type]
                )
            else:
                raise e
        return is_return, return_value

    def __do_raise(self, raise_ast):
        "raise is eagerly evaluated"
        exception_type = self.__eval_expr(raise_ast.get("exception_type"), lazy=False)
        if exception_type.type() != Type.STRING:
            super().error(
                ErrorType.TYPE_ERROR,
                "Raise statement must have a string exception type",
            )

        raise UserException(exception_type.value())

    def __lazify(self, func, lazy):
        "return a lazy version of the function if lazy is True"
        if lazy:
            return Value(Type.FUNC, func)
        return func()

    def __call_func(self, call_node, lazy):
        func_name = call_node.get("name")

        args = []
        for arg in call_node.get("args"):
            result = self.__eval_expr(arg, lazy)  # result is a Value object
            args.append(result)

        if func_name == "print":

            def print_console(args: list[Element]):
                output = ""
                for arg in args:
                    output += get_printable(self.__eval_expr(arg, lazy=False))
                super(self.__class__, self).output(output)
                return Value(Type.NIL, None)

            return self.__lazify(lambda: print_console(args), lazy)
        if func_name == "inputi":
            return self.__lazify(lambda: self.__call_input(func_name, args), lazy)
        if func_name == "inputs":
            return self.__lazify(lambda: self.__call_input(func_name, args), lazy)

        return self.__lazify(
            lambda: self.__run_function(func_name, args, lazy=False), lazy
        )

    def __call_input(self, func_name, args):
        "call inputi() or inputs() function with array of args"
        if len(args) == 1:
            result = self.__eval_expr(args[0], lazy=False)
            super().output(get_printable(result))
        elif len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if func_name == "inputi":
            return Value(Type.INT, int(inp))
        # input string
        if func_name == "inputs":
            return Value(Type.STRING, inp)

    def __assign(self, assign_ast):
        var_name = assign_ast.get("name")
        value_obj = self.__eval_expr(assign_ast.get("expression"), lazy=True)

        # look up variable from current scope up to the closest function scope
        for scope_type, env_iterator in reversed(self.env_scope_stack):
            if env_iterator.get(var_name) is not None:
                env_iterator.set(var_name, value_obj)
                break
            # when reaching the function scope but the variable is not found
            elif scope_type == ScopeType.FUNCTION:
                super().error(
                    ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
                )

    def __var_def(self, var_ast):
        var_name = var_ast.get("name")
        if not self.env_scope_stack.top.create(var_name, Value(Type.INT, 0)):
            super(self.__class__, self).error(
                ErrorType.NAME_ERROR, f"Duplicate definition for variable {var_name}"
            )

    def __arg_def(self, var_name, value):
        """Define a new argument in the current function scope with passed value node"""
        if not self.env_scope_stack.top.create(var_name, value):
            super().error(
                ErrorType.NAME_ERROR,
                f"Duplicate definition for function argument name {var_name}",
            )

    def __get_var_value(self, expr_ast):
        "look up variable from current scope up to the closest function scope, return its value"
        var_name = expr_ast.get("name")
        for scope_type, env_iterator in reversed(self.env_scope_stack):
            val = env_iterator.get(var_name)
            if val is not None:
                return val
            if scope_type == ScopeType.FUNCTION and val is None:
                return Value(
                    Type.FUNC,
                    lambda: super(self.__class__, self).error(
                        ErrorType.NAME_ERROR, f"Variable {var_name} not found"
                    ),
                )

    def __eval_expr(self, expr_ast, lazy):
        if isinstance(expr_ast, Value) and not lazy:
            expr_ast.eval_if_lazy()
            return expr_ast
        if isinstance(expr_ast, Value) and lazy:
            return expr_ast

        if expr_ast is None or expr_ast.elem_type == InterpreterBase.NIL_NODE:
            return Value(Type.NIL, None)
        if expr_ast.elem_type == InterpreterBase.INT_NODE:
            return Value(Type.INT, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.STRING_NODE:
            return Value(Type.STRING, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.BOOL_NODE:
            return Value(Type.BOOL, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.VAR_NODE:
            res = self.__get_var_value(expr_ast)
            if not lazy:
                res.eval_if_lazy()
            return res
        if expr_ast.elem_type == InterpreterBase.FCALL_NODE:
            return self.__call_func(expr_ast, lazy)
        if expr_ast.elem_type in Interpreter.UNARY_OPS:
            return self.__eval_unary_op(expr_ast, lazy)
        if expr_ast.elem_type in Interpreter.BIN_OPS:
            return self.__eval_op(expr_ast, lazy)

    def __eval_unary_op(self, arith_ast, lazy):
        "evaluate unary operation, return a function if it is lazy"
        value_obj = self.__eval_expr(arith_ast.get("op1"), lazy)

        def evaluate(value_obj):
            value_obj.eval_if_lazy()
            if arith_ast.elem_type not in self.op_to_lambda[value_obj.type()]:
                super(self.__class__, self).error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible operator {arith_ast.elem_type} for type {value_obj.type()}",
                )
            f = self.op_to_lambda[value_obj.type()][arith_ast.elem_type]
            return f(value_obj)

        return self.__lazify(lambda: evaluate(value_obj), lazy)

    def __eval_op(self, arith_ast, lazy):
        left_value_obj = self.__eval_expr(arith_ast.get("op1"), lazy=True)
        right_value_obj = self.__eval_expr(arith_ast.get("op2"), lazy=True)

        def calculate(left_value_obj, right_value_obj):
            left_value_obj.eval_if_lazy()

            # Short Circuiting for AND and OR Operators depends on the left value
            if arith_ast.elem_type == "&&" and not left_value_obj.value():
                return Value(Type.BOOL, False)
            if arith_ast.elem_type == "||" and left_value_obj.value():
                return Value(Type.BOOL, True)

            right_value_obj.eval_if_lazy()
            # Special case for == and != operators comparing different types and nil
            if arith_ast.elem_type in Interpreter.BIN_OPS_EXCEPT and (
                not left_value_obj
                or not right_value_obj
                or left_value_obj.type() != right_value_obj.type()
            ):
                if arith_ast.elem_type == "==":
                    return Value(Type.BOOL, False)
                elif arith_ast.elem_type == "!=":
                    return Value(Type.BOOL, True)

            if left_value_obj.type() != right_value_obj.type():
                super(self.__class__, self).error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible types for {arith_ast.elem_type} operation",
                )
            if arith_ast.elem_type not in self.op_to_lambda[left_value_obj.type()]:
                super(self.__class__, self).error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible operator {arith_ast.elem_type} for type {left_value_obj.type()}",
                )
            f = self.op_to_lambda[left_value_obj.type()][arith_ast.elem_type]
            return f(left_value_obj, right_value_obj)

        return self.__lazify(lambda: calculate(left_value_obj, right_value_obj), lazy)

    def __setup_ops(self):
        self.op_to_lambda = {}
        # set up operations on integers
        self.op_to_lambda[Type.INT] = {}
        self.op_to_lambda[Type.INT]["+"] = lambda x, y: Value(
            x.type(), x.value() + y.value()
        )
        self.op_to_lambda[Type.INT]["-"] = lambda x, y: Value(
            x.type(), x.value() - y.value()
        )
        self.op_to_lambda[Type.INT]["*"] = lambda x, y: Value(
            x.type(), x.value() * y.value()
        )
        self.op_to_lambda[Type.INT]["/"] = lambda x, y: Value(
            x.type(), x.value() // y.value()
        )
        self.op_to_lambda[Type.INT][">="] = lambda x, y: Value(
            Type.BOOL, x.value() >= y.value()
        )
        self.op_to_lambda[Type.INT]["<="] = lambda x, y: Value(
            Type.BOOL, x.value() <= y.value()
        )
        self.op_to_lambda[Type.INT][">"] = lambda x, y: Value(
            Type.BOOL, x.value() > y.value()
        )
        self.op_to_lambda[Type.INT]["<"] = lambda x, y: Value(
            Type.BOOL, x.value() < y.value()
        )
        self.op_to_lambda[Type.INT]["=="] = lambda x, y: Value(
            Type.BOOL, x.value() == y.value()
        )
        self.op_to_lambda[Type.INT]["!="] = lambda x, y: Value(
            Type.BOOL, x.value() != y.value()
        )
        # set up operations on strings
        self.op_to_lambda[Type.STRING] = {}
        self.op_to_lambda[Type.STRING]["+"] = lambda x, y: Value(
            x.type(), x.value() + y.value()
        )
        self.op_to_lambda[Type.STRING]["=="] = lambda x, y: Value(
            Type.BOOL, x.value() == y.value()
        )
        self.op_to_lambda[Type.STRING]["!="] = lambda x, y: Value(
            Type.BOOL, x.value() != y.value()
        )
        # set up operations on booleans
        self.op_to_lambda[Type.BOOL] = {}
        self.op_to_lambda[Type.BOOL]["||"] = lambda x, y: Value(
            x.type(), x.value() or y.value()
        )
        self.op_to_lambda[Type.BOOL]["&&"] = lambda x, y: Value(
            Type.BOOL, x.value() and y.value()
        )
        self.op_to_lambda[Type.BOOL]["=="] = lambda x, y: Value(
            Type.BOOL, x.value() == y.value()
        )
        self.op_to_lambda[Type.BOOL]["!="] = lambda x, y: Value(
            Type.BOOL, x.value() != y.value()
        )

        #  unary operations
        self.op_to_lambda[Type.INT]["neg"] = lambda x: Value(Type.INT, -x.value())
        self.op_to_lambda[Type.BOOL]["!"] = lambda x: Value(Type.BOOL, not x.value())

        # nil operations
        self.op_to_lambda[Type.NIL] = {}
        self.op_to_lambda[Type.NIL]["=="] = lambda x, y: Value(Type.BOOL, True)
        self.op_to_lambda[Type.NIL]["!="] = lambda x, y: Value(Type.BOOL, False)
