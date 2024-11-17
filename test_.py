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

struct dog {
 bark: int;
 bite: int;
}

func foo(d: dog) : dog {  /* d holds the same object reference that the koda variable holds */
  d.bark = 10;
  return d;  		/* this returns the same object reference that the koda variable holds */
}

 func main() : void {
  var koda: dog;
  var kippy: dog;
  koda = new dog;
  kippy = foo(koda);	/* kippy holds the same object reference as koda */
  kippy.bite = 20;
  print(koda.bark, " ", koda.bite); /* prints 10 20 */
}


""",
        """
10 20""",
    ],
    [
        """
        struct dog {
  bark: int;
  bite: int;
}

func bar() : int {
  return;  /* no return value specified - returns 0 */
}

func bletch() : bool {
  print("hi");
  /* no explicit return; bletch must return default bool of false */
}

func voo() : void {
  return ; 
}
func boing() : dog {
  return;  /* returns nil */
}

func main() : void {
  voo();
   var val: int;
   val = bar();
   print(val);  /* prints 0 */
   print(bletch()); /* prints false */
   print(boing()); /* prints nil */
}

""",
        """
        0
hi
false
nil
""",
    ],
    [
        """
        struct person {
  name: string;
  age: int;
}

func foo(a:int, b: person) : void {
  return ;
}

func main() : void {
  var x: int;
  x = 5;
  var p:person;
  p = new person;
  p.age = 18;
  print(foo(x, nil));
  print(x);      /* prints 5, since x is passed by value */
  print(p.age);  /* prints 19, since p is passed by object reference */
}
""",
        """
        5
19
""",
    ],
    [
        """
  struct list {
    val: int;
    next: list;
}

func cons(val: int, l: list) : list {
    var h: list;
    h = new list;
    h.val = val;
    h.next = l;
    return h;
}

func rev_app(l: list, a: list) : list {
    if (l == nil) {
        return a;
    }

    return rev_app(l.next, cons(l.val, a));
}

func reverse(l: list) : list {
    var a: list;

    return rev_app(l, a);
}

func print_list(l: list): void {
    var x: list;
    var n: int;
    for (x = l; x != nil; x = x.next) {
        print(x.val);
        n = n + 1;
    }
    print("N=", n);
}

func main() : void {
    var n: int;
    var i: int;
    var l: list;
    var r: list;

    n = inputi();
    for (i = n; i; i = i - 1) {
        var n: int;
        n = inputi();
        l = cons(n, l);
    }
    r = reverse(l);
    print_list(r);
}
  """,
        """
  idk
  """,
    ],
    [
        """
        struct foo {
  i:int;
}

struct bar {
  f:foo;
}

func main() : void {
  var b : bar;
  b = new bar;
  b.f = new foo;
  b.f.i = 10;

  print(b.f.i);
}
/*
*OUT*
10
*OUT*
*/
""",
        """
        10
""",
    ],
    [
        """
        struct foo {
  i:int;
}
       func main() : int {
  print(5 == true);
  print(true == 1);
  print(-5 == true);
  print(0 == false);
  print(0 != true);
  
  var b: foo;
  print(b == nil);
  print(b != nil);
  print(nil == b);
  print(nil != b);
  print(nil == nil);
  print(nil != nil);

}

/*
*OUT*
true
true
true
true
true
*OUT*
*/

""",
        """
""",
    ],
]


def test(program_source, expected_output, debug=False):
    print("=" * 40)
    print("Running test...")
    # print(program_source)
    # this is how you use our parser to parse a valid Brewin program into an AST

    if not debug:
        # redirect the output to a variable
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

    interpreter = Interpreter(trace_output=False)
    interpreter.run(program_source)

    if not debug:
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

    # sys.stdout = old_stdout
    # assert out == clean_output


files = [
    "v3/fails/Structs-Struct_matches_nil_but_not_void.br",
    "v3/tests/Type_Validity-Type_Coercion_With_Operators.br",
    "v3/fails/Type_Validity-Type_Coercion,_input,_shadowing,_and_void_call.br",
]

if __name__ == "__main__":
    # for program, expected_output in tests[-1:]:
    #     test(program, expected_output, True)
    for file in files[-1:]:
        with open(f"fall-24-autograder/{file}", "r") as f:
            test(f.read(), "")
