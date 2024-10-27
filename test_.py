# Derive from InterpreterBase class
# Your Interpreter class MUST implement at least the constructor and the run() method that is used to interpret a Brewin program

from brewparse import parse_program
from element import Element
from interpreter_ import Interpreter


tests = [
    [
        """
func main() {
  var x;   
  x = 5 + 6;
  print("The sum is: ", x);
}
""",
        """The sum is: 11""",
    ],
    [
        """
        func main() {
  var a;
  a = 5 + 10;
  print(a);
  print("that's all!");
}
        """,
        """
15
That's all!
        """,
    ],
    [
        """
        func main() {
  var bar;
  bar = 5;
  print("The answer is: ", (10 + bar) - 6, "!");
}
        """,
        """
        the answer is: 9!
        """,
    ],
    [
        """func main() {
	var foo;
 	var bar;
    var bletch;
    var prompt;
    var boo;
	foo = 10;  
	bar = 3 + foo;
	bletch = 3 - (5 + 2);
	prompt = "enter a number: ";
	boo = inputi();
	boo = inputi("Enter a number: ");
    var b;
    var a;
    b = 4;
    a = b;
    print("hello world!");
    print("the answer is:", b);
    print("the answer is: ", b + (a - 5), "!");	
    var x;
    x = 5 + 6;
    print(x);
    x = "bar"+ "foo";
    print(x);
    x = 3;
    print(x);
    var y;
    var s;
    s = ((5 + (6 - 3)) - ((2 - 3) - (1 - 7)));
    print(s);
    print("x + s -2 = ", (x + s) - 2);
    print("inputi = ", inputi());
}
""",
        """
        11
        barfoo
        3
        3
        x + s -2 = 4
        inputi = ...
        """,
    ],
]


def test(program_source, expected_output):
    print("=" * 40)
    print("Running test...")
    # print(program_source)
    # this is how you use our parser to parse a valid Brewin program into an AST

    interpreter = Interpreter()
    interpreter.run(program_source)

    print("-" * 40)
    print("Expected output:")
    clean_output = expected_output.strip()
    while "\n " in clean_output:
        clean_output = clean_output.replace("\n ", "\n")
    print(clean_output)
    print("=" * 40)


if __name__ == "__main__":
    for program, expected_output in tests:
        test(program, expected_output)
