# Brewin++ Statically-typed Interpreter Project

## Project Overview

The Brewin++ interpreter extends the original Brewin interpreter by introducing several new features, such as static typing, default return values, coercion, and user-defined structures. These additions enhance type safety, control flow, and program structure, building on the foundation of the original interpreter.

The interpreter leverages an **Abstract Syntax Tree (AST)** to parse and execute Brewin++ programs. The AST provides a hierarchical representation of the program, enabling efficient and organized interpretation.

## Abstract Syntax Tree (AST)

The AST is central to the interpreter’s design. Each node represents a distinct language construct, enabling the recursive traversal needed for program execution.

### Core Nodes

- **Program Node**: Represents the overall program, holding all function and struct definitions.
- **Function Definition Nodes**: Encapsulate a function's name, parameter list, return type, and body.
- **Statement Nodes**: Handle control structures like `if` statements, `for` loops, assignments, and returns.
- **Expression Nodes**: Represent arithmetic, boolean, and comparison operations.
- **Variable Nodes**: Represent declared variables in the program.
- **Value Nodes**: Represent constants (e.g., integers, strings, booleans, `nil`).

### New Nodes in Brewin++

- **Struct Definition Node**: Represents user-defined structures and their fields.
- **Field Definition Node**: Defines individual fields within a structure.
- **Extended Function Nodes**: Include return type annotations for static typing.

The AST design ensures precise type checking, dynamic program execution, and support for new language features.

---

## Key Features

### Existing Features from Brewin

1. **Control Structures**:
   - Supports `if` statements and nested `if` statements with mandatory braces.
   - Supports `for` loops, allowing nesting and boolean conditions.

2. **Expressions**:
   - Handles arithmetic operators (`+`, `-`, `*`, `/`) with proper precedence.
   - Supports comparison (`==`, `!=`, `<`, `<=`, `>`, `>=`) and logical operators (`&&`, `||`, `!`).

3. **Function Calls**:
   - Functions can be called within expressions, supporting nesting and parameterized calls.
   - Return statements enable early exit from functions.

4. **Scoping Rules**:
   - Implements lexical scoping to restrict variable visibility to their respective blocks.

5. **Error Handling**:
   - Type errors (`ErrorType.TYPE_ERROR`) for invalid operations.
   - Name errors (`ErrorType.NAME_ERROR`) for undefined variables or fields.

6. **Constants and Variables**:
   - Supports boolean, integer, and string constants, including negative integers.

---

### New Features in Brewin++

1. **Static Typing**:
   - All variables, function parameters, and return types require explicit type annotations.
   - Type mismatches result in a `ErrorType.TYPE_ERROR`.

2. **Default Return Values**:
   - Non-void functions must always return a value. If no explicit return is provided, the interpreter returns the default value for the function's return type:
     - `int`: `0`
     - `bool`: `false`
     - `string`: `""`
     - Struct types: `nil`

3. **Coercion**:
   - Integer-to-boolean coercion:
     - `0` is coerced to `false`.
     - Non-zero integers are coerced to `true`.
   - Supported in assignments, parameter passing, return statements, and control structures like `if` and `for`.

4. **User-Defined Structures**:
   - Structures are defined using `struct`, allowing complex data modeling:
     ```plaintext
     struct Person {
         name: string;
         age: int;
     }
     ```
   - Structures must be allocated with the `new` keyword, and their fields are initialized with default values.
   - Fields are accessed using the dot operator (e.g., `person.name`).

5. **Enhanced Error Handling**:
   - Fault errors (`ErrorType.FAULT_ERROR`) for dereferencing a `nil` object.
   - Name errors (`ErrorType.NAME_ERROR`) for accessing undefined fields in a structure.

6. **Updated Print Function**:
   - The `print()` function can handle all types, including `nil`, and its return type is now `void`.

---

## Usage

1. Install Python 3.11 or later.
2. Clone the project repository or copy all required files to your environment.
3. Run the interpreter:
   ```bash
   python interpreterv3.py <path_to_brewin_program>
   ```


## Licensing and Attribution

This project was developed as part of CS131 Fall 2024 by Carey Nachenberg. See the [CS131 website](https://ucla-cs-131.github.io/fall-24-website/) for more information.
