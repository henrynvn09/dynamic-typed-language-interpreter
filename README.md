# Brewin Interpreter Project
Below is a sample `readme.txt` file based on the requirements and provided instructions. This `readme.txt` includes basic explanations, known issues, usage guidelines, and citations for any external code used.

## Project Overview

The core concept behind this project is the implementation of an interpreter that parses and executes Brewin programs by leveraging an **Abstract Syntax Tree (AST)**. The AST represents the hierarchical structure of the source code, breaking it down into nodes that correspond to different language elements, such as functions, statements, expressions, and variables. This tree-based structure allows for a clean separation between parsing, interpretation, and error handling.

### Abstract Syntax Tree (AST)

The AST is a crucial part of the interpreter’s design. During parsing, the Brewin source code is transformed into an AST where each node represents a construct in the language:
- **Program Node**: Represents the entire Brewin program and holds all function definitions.
- **Function Definition Nodes**: Encapsulate each function’s name, its list of formal parameters, and a series of statements.
- **Statement Nodes**: Represent control structures like if-statements, for-loops, return statements, and print statements.
- **Expression Nodes**: Contain operations, such as arithmetic calculations, boolean expressions, and comparisons.

By building and navigating the AST, the interpreter can efficiently execute each part of the Brewin program. The interpreter uses a **recursive traversal** strategy, where each node type has a corresponding method to evaluate or execute it based on its purpose (e.g., control flow, arithmetic, or logical evaluation).

The recursive nature of the AST traversal allows the interpreter to dynamically manage function calls, variable scoping, and control flow, providing a structured yet flexible way to execute Brewin programs.

### Main Files
- `interpreterv2.py`: The main interpreter file that runs and manages the execution of Brewin programs.
- Supporting modules like `variable.py`, `statement.py`, etc., as needed to handle different types of nodes and features. (These should be detailed with file names if used.)

## Key Features
1. **Control Structures**: Supports if-statements and nested if-statements with required braces. It also handles nested for-loops, ensuring that loop conditions are evaluated as boolean expressions.
2. **Expressions**: Supports arithmetic and logical operators with proper precedence, including:
   - Arithmetic operations: `+`, `-`, `*`, `/` (integer division).
   - Comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.
   - Boolean operations: `||`, `&&`, `!`.
3. **Return Statements**: Handles return statements within functions, ensuring immediate exits from all nested blocks.
4. **Scoping Rules**: Implements lexical scoping, ensuring that variables are accessible only within their respective blocks.
5. **Error Handling**: Implements error types for:
   - Type errors (`ErrorType.TYPE_ERROR`) when conditions or operations involve mismatched or incorrect types.
   - Name errors (`ErrorType.NAME_ERROR`) for variables referenced outside their scope.
6. **Function Calls**: Allows function calls within expressions, supporting complex expressions and nesting.
7. **Constants and Variables**: Allows the use of boolean, integer, and string constants, including handling of negative values.

## Citations
- **External Code Use**: The following code snippet was found and adapted from an online source:
  ```python
  # Citation: The following code was found on stackoverflow.com/questions/12345...
  def example_function():
      pass
  # End of copied code
  ```

## Licensing and Attribution

This is an unlicensed repository; even though the source code is public, it is **not** governed by an open-source license.

This project was developed as part of CS131 Fall 2024 by Carey Nachenberg. See the CS131 website for more information.
