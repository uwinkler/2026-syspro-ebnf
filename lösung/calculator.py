"""Tischrechner mit Variablen und Funktionen.

Vollständige Implementierung in einer Datei. Sprache:

    program     = { statement } ;
    statement   = assignment | fundef | expr_stmt ;
    assignment  = IDENT "=" expr ";" ;
    fundef      = "def" IDENT "(" [ param_list ] ")" "=" expr ";" ;
    param_list  = IDENT { "," IDENT } ;
    expr_stmt   = expr ";" ;
    expr        = term { ("+" | "-") term } ;
    term        = factor { ("*" | "/") factor } ;
    factor      = NUMBER
                | IDENT "(" [ arg_list ] ")"
                | IDENT
                | "(" expr ")" ;
    arg_list    = expr { "," expr } ;
    NUMBER      = digit { digit } [ "." digit { digit } ] ;
    IDENT       = letter { letter | digit | "_" } ;

Aufruf:
    python calculator.py            -> interaktiver Interpreter (REPL)
    python calculator.py datei.calc -> Datei auswerten
    cat datei.calc | python calculator.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

import ply.lex as lex
import ply.yacc as yacc


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

reserved = {"def": "DEF"}

tokens = (
    "NUMBER",
    "IDENT",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "SEMI",
    "ASSIGN",
) + tuple(reserved.values())

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","
t_SEMI = r";"
t_ASSIGN = r"="

t_ignore = " \t"


def t_NUMBER(t):
    r"\d+(\.\d+)?"
    t.value = float(t.value) if "." in t.value else int(t.value)
    return t


def t_IDENT(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "IDENT")
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise SyntaxError(f"Unbekanntes Zeichen {t.value[0]!r} in Zeile {t.lineno}")


lexer = lex.lex()


# ---------------------------------------------------------------------------
# AST-Knoten
# ---------------------------------------------------------------------------


@dataclass
class Num:
    value: int | float


@dataclass
class Var:
    name: str


@dataclass
class BinOp:
    op: str
    left: object
    right: object


@dataclass
class Call:
    name: str
    args: list


@dataclass
class Assign:
    name: str
    expr: object


@dataclass
class FunDef:
    name: str
    params: list[str]
    body: object


@dataclass
class ExprStmt:
    expr: object


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)


def p_program(p):
    """program : statements
               | empty"""
    p[0] = p[1] or []


def p_empty(p):
    "empty :"
    p[0] = []


def p_statements_one(p):
    "statements : statement"
    p[0] = [p[1]]


def p_statements_many(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]


def p_statement_assign(p):
    "statement : IDENT ASSIGN expr SEMI"
    p[0] = Assign(p[1], p[3])


def p_statement_fundef(p):
    "statement : DEF IDENT LPAREN param_list RPAREN ASSIGN expr SEMI"
    p[0] = FunDef(p[2], p[4], p[7])


def p_statement_expr(p):
    "statement : expr SEMI"
    p[0] = ExprStmt(p[1])


def p_param_list_empty(p):
    "param_list :"
    p[0] = []


def p_param_list_one(p):
    "param_list : IDENT"
    p[0] = [p[1]]


def p_param_list_many(p):
    "param_list : param_list COMMA IDENT"
    p[0] = p[1] + [p[3]]


def p_arg_list_empty(p):
    "arg_list :"
    p[0] = []


def p_arg_list_one(p):
    "arg_list : expr"
    p[0] = [p[1]]


def p_arg_list_many(p):
    "arg_list : arg_list COMMA expr"
    p[0] = p[1] + [p[3]]


def p_expr_binop(p):
    """expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr"""
    p[0] = BinOp(p[2], p[1], p[3])


def p_expr_group(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]


def p_expr_number(p):
    "expr : NUMBER"
    p[0] = Num(p[1])


def p_expr_call(p):
    "expr : IDENT LPAREN arg_list RPAREN"
    p[0] = Call(p[1], p[3])


def p_expr_var(p):
    "expr : IDENT"
    p[0] = Var(p[1])


def p_error(p):
    if p is None:
        raise SyntaxError("Unerwartetes Eingabeende")
    raise SyntaxError(
        f"Syntaxfehler bei Token {p.type!r} ({p.value!r}) in Zeile {p.lineno}"
    )


parser = yacc.yacc(debug=False, write_tables=False)


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------


@dataclass
class Interpreter:
    """Hält Variablen und Funktionen über mehrere Eingaben hinweg.

    Damit derselbe Interpreter sowohl für Skripte als auch für die REPL
    verwendet werden kann.
    """

    variables: dict[str, int | float] = field(default_factory=dict)
    functions: dict[str, tuple[list[str], object]] = field(default_factory=dict)

    def eval_expr(self, node, env: dict | None = None):
        if isinstance(node, Num):
            return node.value
        if isinstance(node, Var):
            if env is not None and node.name in env:
                return env[node.name]
            if node.name in self.variables:
                return self.variables[node.name]
            raise NameError(f"Undefinierte Variable: {node.name!r}")
        if isinstance(node, BinOp):
            l = self.eval_expr(node.left, env)
            r = self.eval_expr(node.right, env)
            return {
                "+": lambda: l + r,
                "-": lambda: l - r,
                "*": lambda: l * r,
                "/": lambda: l / r,
            }[node.op]()
        if isinstance(node, Call):
            if node.name not in self.functions:
                raise NameError(f"Undefinierte Funktion: {node.name!r}")
            params, body = self.functions[node.name]
            if len(params) != len(node.args):
                raise TypeError(
                    f"Funktion {node.name!r} erwartet {len(params)} Argumente, "
                    f"erhalten {len(node.args)}"
                )
            local = {p: self.eval_expr(a, env) for p, a in zip(params, node.args)}
            return self.eval_expr(body, local)
        raise SyntaxError(f"Unbekannter AST-Knoten: {node!r}")

    def execute(self, statements) -> list:
        """Führt eine Anweisungsliste aus. Gibt Liste der Ausdrucks-Ergebnisse
        (in Quelltextreihenfolge) zurück."""
        results: list = []
        for stmt in statements:
            if isinstance(stmt, Assign):
                self.variables[stmt.name] = self.eval_expr(stmt.expr)
            elif isinstance(stmt, FunDef):
                self.functions[stmt.name] = (stmt.params, stmt.body)
            elif isinstance(stmt, ExprStmt):
                results.append(self.eval_expr(stmt.expr))
        return results


def parse(source: str):
    """Parst Quelltext und gibt eine Liste von AST-Knoten zurück."""
    return parser.parse(source, lexer=lexer.clone()) or []


def run(source: str, interpreter: Interpreter | None = None):
    """Quelltext auswerten. Gibt das Ergebnis des **letzten** Ausdrucks zurück
    oder ``None``, wenn kein Ausdruck vorkam."""
    interp = interpreter or Interpreter()
    results = interp.execute(parse(source))
    return results[-1] if results else None


# ---------------------------------------------------------------------------
# Hilfsfunktionen für die Ausgabe
# ---------------------------------------------------------------------------


def format_number(n) -> str:
    if isinstance(n, float) and n.is_integer():
        return str(int(n))
    return str(n)


# ---------------------------------------------------------------------------
# Interaktiver Interpreter (REPL)
# ---------------------------------------------------------------------------


REPL_HEADER = """\
Tischrechner.
Mehrere Zeilen sind erlaubt; eine Anweisung endet mit ';'.
Befehle: :vars  :funcs  :reset  :help  :quit (oder Strg-D)
"""


def repl():
    interp = Interpreter()
    print(REPL_HEADER)
    buffer = ""
    primary = ">>> "
    secondary = "... "
    while True:
        try:
            line = input(primary if not buffer else secondary)
        except EOFError:
            print()
            return
        except KeyboardInterrupt:
            print("^C")
            buffer = ""
            continue

        stripped = line.strip()

        # Spezialbefehle nur am Anfang einer Eingabe
        if not buffer and stripped.startswith(":"):
            cmd = stripped.lower()
            if cmd in (":quit", ":q", ":exit"):
                return
            if cmd in (":help", ":h", "?"):
                print(REPL_HEADER)
            elif cmd == ":vars":
                if not interp.variables:
                    print("(keine Variablen)")
                for name, value in interp.variables.items():
                    print(f"  {name} = {format_number(value)}")
            elif cmd == ":funcs":
                if not interp.functions:
                    print("(keine Funktionen)")
                for name, (params, _) in interp.functions.items():
                    print(f"  {name}({', '.join(params)})")
            elif cmd == ":reset":
                interp = Interpreter()
                print("Variablen und Funktionen gelöscht.")
            else:
                print(f"Unbekannter Befehl: {stripped}")
            continue

        buffer += line + "\n"

        # Auf abgeschlossene Anweisung warten (mindestens ein ';' enthalten).
        if ";" not in buffer:
            continue

        try:
            results = interp.execute(parse(buffer))
        except SyntaxError as e:
            # Vermutlich unvollständig? Wir brechen schlicht ab und melden
            # den Fehler – der Nutzer kann es erneut versuchen.
            print(f"Syntaxfehler: {e}")
        except Exception as e:  # NameError, TypeError, ZeroDivisionError, ...
            print(f"Fehler: {e}")
        else:
            for r in results:
                print(format_number(r))
        finally:
            buffer = ""


# ---------------------------------------------------------------------------
# Einstiegspunkt
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv and sys.stdin.isatty():
        repl()
        return

    if argv:
        with open(argv[0], "r", encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.read()

    interp = Interpreter()
    try:
        results = interp.execute(parse(source))
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        sys.exit(1)
    for r in results:
        print(format_number(r))


if __name__ == "__main__":
    main()
