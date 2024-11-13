# Derive from InterpreterBase class
# Your Interpreter class MUST implement at least the constructor and the run() method that is used to interpret a Brewin program

from brewparse import parse_program
from element import Element
from interpreter_ import Interpreter
from io import StringIO  # Python3 use:
import sys

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
  print("That's all!");
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
        The answer is: 9!
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
	boo = 7;
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
    print("inputi = ", 7);
}
""",
        """
        hello world!\nthe answer is:4\nthe answer is: 3!\n11\nbarfoo\n3\n3\nx + s -2 = 4\ninputi = 7
        """,
    ],
    [
        """
        func bar(a) {
  print(a);
}
func bar(a,b) {
    print(a+b);
}
func main() {
  bar(5);
  bar("hi");
  bar(true || false);
    bletch(1,3,2+4);
}
func bletch(a,b,c) {
  print("The answer is: ", a+b*c);
}

""",
        """
        5
hi
true
The answer is: 19""",
    ],
    [
        """
        func bar(a) {
  print(a);
}
func bar(a,b) {
    print(a+b);
}
func main() {
  bar(5);
  bar("hi");
  bar(1+2);
    bletch(1,3,2+4);
}
func bletch(a,b,c) {
  print("The answer is: ", a+b*c);
}
""",
        "5\nhi\n3\nThe answer is: 19",
    ],
    [
        """
        func bar(a) {
  return a+1;
}
func main() {
  print(false || true);
  print(false && true);
  print(false == true);
    print(false != true);
    print(!(false == true));
    print(true || false);  /* prints true */
print(true || false && false); /* prints true */
print(5/3);            /* prints 1 */
print(-6);             /* prints -6 */
print(!true);          /* prints false */

var a;
a = 3;
print(a > 5);          /* prints false */
print("abc"+"def");    /* prints abcdef */

print("abc"==3);    /* prints false */
print("abc"!=23);    /* prints true */

}

""",
        """
        true
false
false
true
true
true
true
1
-6
false
false
abcdef
false
true
""",
    ],
    [
        """
      func foo() { 
 print("hello");
 /* no explicit return command */
}

func bar(a) {
  return a;  /* no return value specified */
}

func main() {
   var val;
   val = nil;
   print("hello");
   if (bar(3) != 2) { print("this should print!"); }
}

""",
        "hello\nthis should print!",
    ],
    [
        """
func bar(a) {
  if (a == 0) { return; }
  if (a == 1) { return 1; }
  if (a == 2) { return 5*a; }
  if (a == 3) { return true; }
  if (a == 4) { return nil; }
}
func foo(x) {
  if (x < 0) {
    print(x);
    return -x;
    print("this will not print");
  }
  print("this will not print either");
  return 5*x;
}
func f(x) {
  return x;
}

func main() {
  print(bar(0));
  print(bar(1));
  print(bar(2));
  print(bar(3));
  print(bar(4));
  print(bar(5));
  print("the positive value is ", foo(-1));
  var x;
  x = 16;
  if (f(x) > 5) {
  print(x);
  if (x < 30 && x > 10) {
    print(3*x);
  }
}
if (f(x) > 0) {
  print(x);
} else {
  print(-x);
}

}

""",
        "nil\n1\n10\ntrue\nnil\nnil\n-1\nthe positive value is 1\n16\n48\n16",
    ],
    [
        """
      func recursion(x) {
  if (x == 0) {
    return 0;
  }
  return x + recursion(x-1);
}
      func main() {
        var x;
        x = "x";
        if (print(x) == nil) {
          print("this should print");
        }
        print(recursion(5));
      }
      """,
        "x\nthis should print\n15",
    ],
    [
        """
      func main() {
  var a;
  a = 5;        /* variable a's scope is the function's block */
  if (a == 5) {
      var b;
      b = 10;   /* variable b's scope is the if block */
      a = 6;
  } /* variable b goes out of scope */
  print(a); /* works fine since a is still in scope, prints 6 */
} /* variable a goes out of scope */

      """,
        "6",
    ],
    [
        """
func foo(c) { 
  if (c == 10) {
    var c;     /* variable of the same name as parameter c */
    c = "hi";
    print(c);  /* prints "hi"; the inner c shadows the parameter c*/
  }
  print(c); /* prints 10 */
}

func main() {
  var a;
  a = 5;
  foo(10);
}


""",
        "hi\n10",
    ],
    [
        """
func main() {
var i;
for (i=0; i+3 < 5; i=i+1) {
  print(i);
}

}


""",
        "0\n1",
    ],
    [
        """
     func foo() {
 print(1);
}

func bar() {
 return nil;
}

func main() {
 var x;
 x = foo();
 if (x == nil) {
  print(2);
 }
 var y;
 y = bar();
 if (y == nil) {
  print(3);
 }
 
}

/*
*OUT*
1
2
3
*OUT*
*/
     """,
        "1\n2\n3",
    ],
    [
        """
func compute() {
    var i;
    for (i = 1; i <= 5; i = i + 1) {
        var j;
        for (j = 1; j <= 5; j = j + 1) {
            if (i * j == 6) {
                return i * 10 + j;
            }
        }
    }
    return -1;
}

func main() {
    print(compute());
}   """,
        "23",
    ],
    [
        """
       func main() : void {
            var eyeballs: int;
            var theory: string;
            var old: bool;
            var n: node;  /* assuming we have defined a node structure - see below */
            print(foo());
            print(bar());
        }

        func foo() : int {
          return; /* returns 0 */
        }

        func bar() : bool {
          print("bar");
        }  /* returns false*/
""",
        """
0
bar
false
""",
    ],
]


def test(program_source, expected_output):
    print("=" * 40)
    print("Running test...")
    # print(program_source)
    # this is how you use our parser to parse a valid Brewin program into an AST

    # redirect the output to a variable
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    interpreter = Interpreter()
    interpreter.run(program_source)

    out = mystdout.getvalue().strip()

    # redirect the output back to stdout
    sys.stdout = old_stdout
    print(out)
    print("-" * 40)
    print("Expected output:")
    clean_output = expected_output.strip()
    while "\n " in clean_output:
        clean_output = clean_output.replace("\n ", "\n")
    print(clean_output)
    print("=" * 40)
    sys.stdout = old_stdout
    # assert out == clean_output


if __name__ == "__main__":
    for program, expected_output in tests[-1:]:
        test(program, expected_output)
