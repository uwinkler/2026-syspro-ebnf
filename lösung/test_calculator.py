import pytest

from calculator import Interpreter, parse, run


# --- Teil 1: Arithmetik ----------------------------------------------------


def test_addition():
    assert run("1 + 2;") == 3


def test_precedence():
    assert run("2 + 3 * 4;") == 14


def test_parentheses():
    assert run("(2 + 3) * 4;") == 20


def test_division_returns_float():
    assert run("10 / 4;") == 2.5


def test_left_assoc():
    assert run("1 - 2 - 3;") == -4


# --- Teil 2: Variablen -----------------------------------------------------


def test_variable_assignment():
    assert run("x = 10; y = 5; x + y;") == 15


def test_variable_chain():
    assert run("a = 2; b = a * 3; b + 1;") == 7


def test_decimal_variable():
    assert run("pi = 3.14; pi * 2;") == 6.28


def test_undefined_variable():
    with pytest.raises(NameError):
        run("z;")


def test_only_assignment_returns_none():
    assert run("x = 1;") is None


# --- Teil 3: Funktionen ----------------------------------------------------


def test_main_example():
    src = """
        x = 1;
        y = 2;
        def sum(a, b) = a + b;
        def mul(a, b) = a * b;
        mul(sum(x, y), sum(x, y));
    """
    assert run(src) == 9


def test_square():
    assert run("def square(n) = n * n; square(7);") == 49


def test_avg():
    assert run("def avg(a,b) = (a+b)/2; avg(3,4);") == 3.5


def test_function_using_function():
    assert run("def f(x) = x + 1; def g(x) = f(x) * 2; g(5);") == 12


def test_function_uses_global():
    assert run("k = 10; def addk(x) = x + k; addk(5);") == 15


def test_local_scope_does_not_leak():
    src = "a = 100; def f(a) = a + 1; f(5); a;"
    assert run(src) == 100


def test_undefined_function():
    with pytest.raises(NameError):
        run("foo(1);")


def test_wrong_arity():
    with pytest.raises(TypeError):
        run("def f(a,b) = a+b; f(1);")


# --- Persistenter Interpreter (für REPL) -----------------------------------


def test_interpreter_persists_state():
    interp = Interpreter()
    assert run("x = 5;", interp) is None
    assert run("def double(n) = n * 2;", interp) is None
    assert run("double(x);", interp) == 10


# --- Parser liefert AST ----------------------------------------------------


def test_parse_returns_statements():
    stmts = parse("1+2; def f(x)=x; f(3);")
    assert len(stmts) == 3
