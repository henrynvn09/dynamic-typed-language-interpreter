# Brewin# Interpreter Project

## Project Overview

The Brewin# Interpreter Project implements a robust interpreter capable of parsing and executing Brewin programs. It supports core features of the Brewin language along with enhancements introduced in Brewin#. These enhancements include **lazy evaluation**, **exception handling**, and **short-circuiting**, building on the foundational features implemented in earlier versions.

The interpreter leverages an **Abstract Syntax Tree (AST)** for structured program parsing, execution, and error handling.

## Abstract Syntax Tree (AST)

The AST structures the Brewin program into hierarchical nodes, each representing a language construct. The interpreter recursively traverses the AST to execute the program, dynamically handling variables, functions, and control flow.

Key node types include:

- **Program Node**: Represents the entire program, encompassing all functions.
- **Function Definition Nodes**: Define functions with parameters and statements.
- **Statement Nodes**: Handle control structures, such as loops, conditionals, and return statements.
- **Expression Nodes**: Manage arithmetic, logical, and comparison operations.

## Features

### New Features in Brewin#

[Specification](CS131 Fall 24 Project #4.pdf)

1. **Lazy Evaluation**:
   - Expressions are evaluated only when their values are required, improving efficiency.
   - Results of evaluated expressions are cached for reuse.
2. **Exception Handling**:

   - `raise` statements and `try/catch` blocks support error handling.
   - Built-in `div0` exception for division by zero.

3. **Short-Circuiting**:

   - Logical operators `&&` and `||` evaluate only as much as needed to determine results.
   - Avoids unnecessary evaluations, optimizing performance.

4. **Enhanced Control Structures**:

   - Nested if-statements and for-loops with boolean conditions.
   - Support for nested try/catch blocks.

5. **Function Calls with Lazy Evaluation**:

   - Function arguments are lazily evaluated only when needed.
   - Functions support returning values and recursion.

6. **Built-in Functions**:
   - `print`, `inputs`, and `inputi` are implemented with eager evaluation for arguments.

### Features from Previous Versions

[Specification](CS131 Fall 24 Project #2.pdf)

1. **Basic Brewin Language Constructs**:

   - Variable declarations and assignments.
   - Support for integer, boolean, and string data types.

2. **Arithmetic and Logical Operations**:

   - Arithmetic: `+`, `-`, `*`, `/` (integer division).
   - Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`.
   - Logical: `||`, `&&`, `!`.

3. **Control Flow**:

   - If-statements and for-loops with proper scoping and nested support.
   - Return statements to exit functions and pass values.

4. **Lexical Scoping**:

   - Variables are accessible only within their defined scope.
   - Nested blocks follow strict scoping rules.

5. **Error Handling**:
   - `ErrorType.TYPE_ERROR` for type mismatches.
   - `ErrorType.NAME_ERROR` for undefined variables or invalid references.

## Usage Instructions

1. Add your Brewin# code to `generate_test.br`.
2. Run the interpreter:
   ```bash
   python3 generate_test.py
   ```
3. Create a symbolic link to the autograder folder:
   ```bash
   ln -s ../interpreter_.py interpreterv4.py
   ```
4. Use the autograder:
   ```bash
   python tester.py 4
   ```

## Testing Features

The interpreter supports robust testing using `tester.py` and custom test cases. These tests validate features such as lazy evaluation, short-circuiting, and exception handling. Users are encouraged to write additional test cases to ensure correctness and explore edge cases.

## Licensing and Attribution

This repository is **unlicensed** and developed as part of CS131 Fall 2024. While the source code is public, it is not governed by any open-source license. The project was created for specification on [Brewin#](CS131 Fall 24 Project #2.pdf) and [Brewin#](CS131 Fall 24 Project #4.pdf) of CS131 Fall 2024 by Carey Nachenberg. For more details, visit the CS131 website.
