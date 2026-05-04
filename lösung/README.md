Hinweis: diese Lösung wurde von Claude Opus 4.7 erzeugt.

# Lösung – Tischrechner mit EBNF und PLY

Vollständige Musterlösung`: [calculator.py](calculator.py).
Implementiert sind alle drei Teile der Aufgabe (Arithmetik, Variablen,
Funktionen) sowie ein interaktiver Interpreter (REPL).

## Setup

```bash
uv sync
```

## Verwendung

### Interaktiver Modus (REPL)

```bash
uv run python calculator.py
```

```
>>> x = 1;
>>> y = 2;
>>> def sum(a, b) = a + b;
>>> def mul(a, b) = a * b;
>>> mul(sum(x, y), sum(x, y));
9
>>> :vars
  x = 1
  y = 2
>>> :funcs
  sum(a, b)
  mul(a, b)
>>> :quit
```

REPL-Befehle: `:vars`, `:funcs`, `:reset`, `:help`, `:quit` (oder `Strg-D`).
Mehrzeilige Eingaben sind erlaubt; eine Anweisung endet mit `;`.

### Datei oder Pipe

```bash
uv run python calculator.py programm.calc
echo "def f(a,b)=a+b; f(1,2);" | uv run python calculator.py
```

## Tests

```bash
uv run pytest -v
```

## EBNF

Die vollständige Grammatik steht im Modul-Docstring von
[calculator.py](calculator.py) und gilt für alle drei Teile.
