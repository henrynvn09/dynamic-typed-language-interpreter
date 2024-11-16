# Add to spec:
# - printing out a nil value is undefined

from env_ import EnvironmentManager
from type_value_ import (
    Type,
    Value,
    get_printable,
    is_generic_type,
    is_non_nil_generic_type,
)
from intbase import InterpreterBase, ErrorType
from brewparse import parse_program
from element import Element
from copy import copy
from struct_ import Struct


class ScopeType:
    FUNCTION = "function"
    BLOCK = "block"


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
        self.variable_scope_stack = []  # stack of function call
        self.env: EnvironmentManager = (
            None  # EnvironmentManager of the current function scope
        )
        self.structure_table = dict()  # dictionary of structure names to their struct

    # run a program that's provided in a string
    # usese the provided Parser found in brewparse.py to parse the program
    # into an abstract syntax tree (ast)
    def run(self, program):
        ast = parse_program(program)
        self.__set_up_function_table(ast)
        self.__set_up_structure_table(ast.get("structs"))
        self.__run_function("main")

    def __set_up_structure_table(self, structs):
        """Structure table is a dictionary of (structure_name, struct_object)"""
        for struct_def in structs:
            fields = dict()
            self.structure_table[struct_def.get("name")] = fields

            for field in struct_def.get("fields"):
                # if the field type is not defined, raise an error
                if (
                    not is_generic_type(field.get("var_type"))
                    and field.get("var_type") not in self.structure_table
                ):
                    super().error(
                        ErrorType.TYPE_ERROR, f"Unknown type {field} for field"
                    )
                else:
                    fields[field.get("name")] = field.get("var_type")

    def __run_function(self, func_name, passed_arguments: list[Element] = []):
        """run a function based on name and list of arguments"""
        func_def: Element = self.__get_func(func_name, passed_arguments)
        evaluated_args = [
            copy(self.__eval_expr(arg, arg_def.get("var_type")))
            for arg, arg_def in zip(passed_arguments, func_def.get("args"))
        ]

        # check if the type of the arguments passed in matches the type of the arguments in the function definition
        for val, arg_type in zip(evaluated_args, func_def.get("args")):
            if val.type() != arg_type.get("var_type"):
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Argument type mismatch in function {func_name} and argument {arg_type.get('name')}",
                )

        self.__create_new_function_scope(
            func_def.get("name"), func_def.get("args"), evaluated_args
        )
        has_return, return_val = self.__run_statements(
            func_def.get("statements"), func_def.get("return_type")
        )

        # if the function return_type is void, it must not have return value
        if func_def.get("return_type") == Type.NIL and return_val is None:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Function {func_name} must return a value of type {func_def.get('return_type')}",
            )

        # if the function return_type is not void, and there is no return statement or no specific return value
        if func_def.get("return_type") != InterpreterBase.VOID_DEF and (
            not has_return or return_val is None
        ):
            return_val = self.__create_default_value_obj(func_def.get("return_type"))

        # if the function return_type is not void, and return type isn't match
        if func_def.get("return_type") != InterpreterBase.VOID_DEF and (
            return_val.type() != func_def.get("return_type")
        ):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Function {func_name} must return a value of type {func_def.get('return_type')}",
            )

        self.__destroy_top_scope()
        return return_val if return_val is not None else Value(Type.NIL, None)

    def __create_new_function_scope(self, func_name, args, values):
        """Initialize new variable scope for a function"""
        self.variable_scope_stack.append((ScopeType.FUNCTION, EnvironmentManager()))
        # current environment is top of stack
        self.env = self.variable_scope_stack[-1][1]
        for arg, value in zip(args, values):
            self.__arg_def(arg.get("name"), value)

    def __create_new_block_scope(self):
        """Initialize new variable scope for a block"""
        self.variable_scope_stack.append((ScopeType.BLOCK, EnvironmentManager()))
        self.env = self.variable_scope_stack[-1][1]

    def __destroy_top_scope(self):
        """Destroy the current function scope, doesn't check errors"""
        self.variable_scope_stack.pop()
        self.env = (
            self.variable_scope_stack[-1][1] if self.variable_scope_stack else None
        )

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

    def __run_statements(self, statements, return_type):
        "if there is a return statement, return True, value. otherwise return False, None"
        # create a block scope
        self.__create_new_block_scope()

        for statement in statements:
            if self.trace_output:
                print(statement)
            if statement.elem_type == InterpreterBase.FCALL_NODE:
                self.__call_func(statement)
            elif statement.elem_type == "=":
                self.__assign(statement)
            elif statement.elem_type == InterpreterBase.VAR_DEF_NODE:
                self.__var_def(statement)
            elif statement.elem_type == InterpreterBase.IF_NODE:
                is_return, return_value = self.__if_condition(statement, return_type)
                if is_return:
                    self.__destroy_top_scope()
                    return is_return, return_value
            elif statement.elem_type == InterpreterBase.RETURN_NODE:
                self.__destroy_top_scope()
                return True, self.__return_value(statement, return_type)
            elif statement.elem_type == InterpreterBase.FOR_NODE:
                is_return, return_value = self.__for_loop(statement, return_type)
                if is_return:
                    self.__destroy_top_scope()
                    return is_return, return_value

        # destroy block scope
        self.__destroy_top_scope()
        return False, None

    def __return_value(self, return_ast, return_type):
        value = self.__eval_expr(return_ast.get("expression"), return_type)
        return value

    def __for_loop(self, for_ast, return_type):
        init = for_ast.get("init")
        condition = for_ast.get("condition")
        update = for_ast.get("update")
        statements = for_ast.get("statements")

        self.__create_new_block_scope()
        self.__assign(init)

        if self.__eval_expr(condition, Type.BOOL).type() != Type.BOOL:
            super().error(
                ErrorType.TYPE_ERROR, "for condition must be a boolean expression"
            )

        while self.__eval_expr(condition, Type.BOOL).value():
            is_return, return_value = self.__run_statements(statements, return_type)
            if is_return:
                self.__destroy_top_scope()
                return is_return, return_value
            self.__run_statements([update], return_type)
        self.__destroy_top_scope()
        return False, None

    def __if_condition(self, if_ast, return_type):
        condition = self.__eval_expr(if_ast.get("condition"), Type.BOOL)
        if condition.type() != Type.BOOL:
            super().error(
                ErrorType.TYPE_ERROR, "If condition must be a boolean expression"
            )
        statements = if_ast.get("statements")
        else_statements = (
            if_ast.get("else_statements") if if_ast.get("else_statements") else []
        )
        if condition.value():
            is_return, return_value = self.__run_statements(statements, return_type)
        else:
            is_return, return_value = self.__run_statements(
                else_statements, return_type
            )
        return is_return, return_value

    def __call_func(self, call_node):
        func_name = call_node.get("name")
        func_args = call_node.get("args")

        if func_name == "print":
            return self.__call_print(call_node)
        if func_name == "inputi":
            return self.__call_input(call_node)
        if func_name == "inputs":
            return self.__call_input(call_node)

        return self.__run_function(func_name, func_args)

    def __call_print(self, call_ast):
        output = ""
        for arg in call_ast.get("args"):
            result = self.__eval_expr(arg, None)  # result is a Value object
            output = output + get_printable(result)
        super().output(output)

    def __call_input(self, call_ast):
        args = call_ast.get("args")
        if args is not None and len(args) == 1:
            result = self.__eval_expr(args[0], None)
            super().output(get_printable(result))
        elif args is not None and len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR, "No inputi() function that takes > 1 parameter"
            )
        inp = super().get_input()
        if call_ast.get("name") == "inputi":
            return Value(Type.INT, int(inp))
        # input string
        if call_ast.get("name") == "inputs":
            return Value(Type.STRING, inp)

    def __assign(self, assign_ast):
        var_name = assign_ast.get("name")
        value_obj = self.__eval_expr(assign_ast.get("expression"), None)

        # look up variable from current scope up to the closest function scope
        for scope_type, env_iterator in reversed(self.variable_scope_stack):
            if "." in var_name:
                var_var, field_name = var_name.split(".", 1)
                var = env_iterator.get(var_var)
            else:
                var = env_iterator.get(var_name)

            if var is not None:
                # try setting the value to var, if it fails, it's a type error
                try:
                    if "." not in var_name:
                        value_obj = self.coerce_value(value_obj, var.type())
                        env_iterator.set(var_name, value_obj)
                    else:
                        struct_ast = env_iterator.get(var_var)
                        value_ast = self.__get_struct_field_obj(struct_ast, field_name)
                        value_obj = self.coerce_value(value_obj, value_ast.type())

                        # TODO: check if necessary
                        if value_ast.type() != value_obj.type():
                            raise TypeError(
                                f"Cannot assign value of type for struct attribute {value_obj.type()} to {value_ast.type()}"
                            )
                        value_ast.set_value(value_obj.value())
                    break
                except TypeError as e:
                    super().error(ErrorType.TYPE_ERROR, str(e))
            # when reaching the function scope but the variable is not found
            elif scope_type == ScopeType.FUNCTION:
                super().error(
                    ErrorType.NAME_ERROR, f"Undefined variable {var_name} in assignment"
                )

    def __var_def(self, var_ast):
        var_name = var_ast.get("name")
        var_type = var_ast.get("var_type")

        default_value = self.__create_default_value_obj(var_type)

        if not self.env.create(var_name, default_value):
            super().error(
                ErrorType.NAME_ERROR, f"Duplicate definition for variable {var_name}"
            )

    def __arg_def(self, var_name, value):
        """Define a new argument in the current function scope with passed value node"""
        if not self.env.create(var_name, value):
            super().error(
                ErrorType.NAME_ERROR,
                f"Duplicate definition for function argument name {var_name}",
            )

    def coerce_value(self, value: Value, target: Type) -> Value:
        if not target:
            return value
        if value.type() == target:
            return value

        if value.type() == Type.INT and target == Type.BOOL:
            return Value(Type.BOOL, value.value() != 0)

        if not is_generic_type(target) and value.type() == Type.NIL:
            return Value(target, None)

        super().error(
            ErrorType.TYPE_ERROR,
            f"Cannot coerce value of type {value.type()} to type {target}",
        )

    def __eval_expr(self, expr_ast, target_type) -> Value:
        if expr_ast is None:
            # TODO: check if this is correct
            return self.__create_default_value_obj(target_type)
        if expr_ast.elem_type == InterpreterBase.NIL_NODE:
            return Value(Type.NIL, None)
        if expr_ast.elem_type == InterpreterBase.INT_NODE:
            res = Value(Type.INT, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.STRING_NODE:
            return Value(Type.STRING, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.BOOL_NODE:
            return Value(Type.BOOL, expr_ast.get("val"))
        if expr_ast.elem_type == InterpreterBase.VAR_NODE:
            var_name = expr_ast.get("name")
            # look up variable from current scope up to the closest function scope
            for scope_type, env_iterator in reversed(self.variable_scope_stack):
                if "." in var_name:
                    var_var, field_name = var_name.split(".", 1)
                    var = env_iterator.get(var_var)
                else:
                    var = env_iterator.get(var_name)
                if var is not None:
                    if "." in var_name:
                        res = self.__get_struct_field_obj(var, field_name)
                        return self.coerce_value(res, target_type)

                    else:
                        return self.coerce_value(var, target_type)
                if scope_type == ScopeType.FUNCTION and var is None:
                    super().error(
                        ErrorType.NAME_ERROR, f"Variable {var_name} not found"
                    )
        if expr_ast.elem_type == InterpreterBase.FCALL_NODE:
            res = self.__call_func(expr_ast)
        if expr_ast.elem_type in Interpreter.UNARY_OPS:
            res = self.__eval_unary_op(expr_ast)
        if expr_ast.elem_type in Interpreter.BIN_OPS:
            res = self.__eval_op(expr_ast)
        if expr_ast.elem_type == InterpreterBase.NEW_NODE:
            res = self.__new_struct(expr_ast)

        return self.coerce_value(res, target_type)

    def __eval_unary_op(self, arith_ast):
        value_obj = self.__eval_expr(arith_ast.get("op1"), Type.BOOL)
        if arith_ast.elem_type not in self.op_to_lambda[value_obj.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {arith_ast.elem_type} for type {value_obj.type()}",
            )
        f = self.op_to_lambda[value_obj.type()][arith_ast.elem_type]
        return f(value_obj)

    def __is_struct(self, value: Value) -> bool:
        return value.type() in self.structure_table

    def __struct_eval_op(self, arith_ast, left_value_obj, right_value_obj):
        if is_non_nil_generic_type(left_value_obj.type()) or is_non_nil_generic_type(
            right_value_obj.type()
        ):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Cannot compare struct with non-struct type other than nil",
            )

        if arith_ast.elem_type in ["==", "!="]:
            # if one of the values is nil, return the opposite of the other value
            if left_value_obj.type() != right_value_obj.type():
                return Value(
                    Type.BOOL, left_value_obj.value() == right_value_obj.value()
                )
            # if both values are structs, compare their references
            return Value(Type.BOOL, left_value_obj.value() is right_value_obj.value())

    def __eval_op(self, arith_ast):
        left_value_obj = self.__eval_expr(arith_ast.get("op1"), None)
        right_value_obj = self.__eval_expr(arith_ast.get("op2"), None)

        if left_value_obj == None or right_value_obj == None:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Cannot compare void value",
            )

        if self.__is_struct(left_value_obj) or self.__is_struct(right_value_obj):
            return self.__struct_eval_op(arith_ast, left_value_obj, right_value_obj)

        if left_value_obj.type() == Type.BOOL and right_value_obj.type() == Type.INT:
            right_value_obj = self.coerce_value(right_value_obj, Type.BOOL)
        if right_value_obj.type() == Type.BOOL and left_value_obj.type() == Type.INT:
            left_value_obj = self.coerce_value(left_value_obj, Type.BOOL)

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
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible types for {arith_ast.elem_type} operation",
            )
        if arith_ast.elem_type not in self.op_to_lambda[left_value_obj.type()]:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Incompatible operator {arith_ast.elem_type} for type {left_value_obj.type()}",
            )
        f = self.op_to_lambda[left_value_obj.type()][arith_ast.elem_type]
        return f(left_value_obj, right_value_obj)

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

    def __create_default_value_obj(self, val_type):
        if val_type == Type.INT:
            return Value(Type.INT, 0)
        if val_type == Type.STRING:
            return Value(Type.STRING, "")
        if val_type == Type.BOOL:
            return Value(Type.BOOL, False)
        if val_type == Type.NIL:
            return Value(Type.NIL)

        if val_type in self.structure_table:
            return Value(val_type)
        if val_type == InterpreterBase.VOID_DEF:
            return None

        # This should never happen
        super().error(ErrorType.TYPE_ERROR, f"Unknown type {val_type}")
        return None

    def __new_struct(self, ast):
        """Generating a new struct object from the AST"""
        struct_type = ast.get("var_type")
        if struct_type not in self.structure_table:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Unknown struct {ast.get('var_type')} on new operation",
            )

        struct_obj = Struct(
            self.structure_table[struct_type], self.__create_default_value_obj
        )
        return Value(struct_type, struct_obj)

    def __get_struct_field_obj(self, struct_ast, field_name):
        if struct_ast.is_NIL():
            super().error(
                ErrorType.FAULT_ERROR,
                f"Cannot access field {field_name} of nil struct",
            )

        obj_type, struct_obj = struct_ast.type(), struct_ast.value()
        if not isinstance(struct_obj, Struct):
            super().error(
                ErrorType.TYPE_ERROR,
                f"Expected struct object, got {obj_type} for .{field_name}",
            )

        field_name += "."

        while field_name:
            current_field, field_name = field_name.split(".", 1)

            try:
                if isinstance(struct_obj, Value):
                    struct_obj = struct_obj.value().get_field(current_field)
                else:
                    struct_obj = struct_obj.get_field(current_field)
            except AttributeError as e:
                super().error(ErrorType.NAME_ERROR, str(e))

        return struct_obj
