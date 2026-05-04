# Aufgabe: Tischrechner mit Variablen und Funktionen (PLY)

## Hintergrund

Im Teil 2 von _NAND2Tetris_ wird eine vollständige
Java-ähnliche Programmiersprache mit Compiler, ... entwickelt.
Das ist sehr lehrreich, aber auch ziemlich umfangreich.

Wir halten es bewusst einfach: Wir entwerfen eine kleine,
selbst definierte Programmiersprache, mit der man Programme der folgenden
Art schreiben kann:

```
x = 1;
y = 2;
def sum(a, b) = a + b;
def mul(a, b) = a * b;
mul(sum(x, y), sum(x, y));
```

Wir verzichten bewusst auf Kontrollfluss (if, while, ...) oder ander high-level Features.

Ziel ist am Ende des Kurses ein Compiler zu schreiben, der solche Programme in HACK-Assembler
und via dem Assembler - den sie ja schon entwicklet haben sollten - in ein HACK Binary
übersetzt – das Ergebnis der letzten Expression soll dann im Register `R[0]`
landen.

In diesem Aufgabenteil geht es jedoch noch nicht um Codegenerierung,
sondern um den **Frontend-Teil** eines Compilers: Wir beschreiben die Sprache
formal mit einer **EBNF-Grammatik** und implementieren einen passenden
**Lexer** und **Parser** in einem Programmiersprache ihrer Wahl (z.B. Python).

---

## Überblick

Sie entwickeln einen Tischrechner, am besten in in aufbauenden Schritten. Jede Stufe erweitert die vorherige:

| Stufe      | Inhalt                             | Beispiel                      |
| ---------- | ---------------------------------- | ----------------------------- |
| **Teil 1** | Zahlen, Grundrechenarten, Klammern | `(2 + 3) * 4 - 1;`            |
| **Teil 2** | Variablen und Zuweisungen          | `x = 5; x * 2;`               |
| **Teil 3** | Funktionsdefinitionen und -aufrufe | `def sum(a,b)=a+b; sum(1,2);` |

---

## Allgemeine technische Hinweise

### PLY

**PLY** (_Python Lex-Yacc_) ist eine reine Python-Umsetzung der klassischen
Unix-Werkzeuge **lex** (Lexer-Generator) und **yacc** (Parser-Generator).
Lexer-Regeln werden als Variablen oder Funktionen mit dem Präfix `t_`
geschrieben, Grammatikregeln als Funktionen mit dem Präfix `p_`, deren
Docstring die Regel in BNF-Notation enthält. PLY erzeugt daraus zur Laufzeit
einen LALR(1)-Parser.

- Dokumentation: <https://www.dabeaz.com/ply/ply.html>
- Quellcode/PyPI: <https://pypi.org/project/ply/>

# Teil 1 – Einfacher Rechner (Zahlen + Grundrechenarten)

## Aufgabe

Implementieren Sie einen Rechner, der einen arithmetischen Ausdruck einliest, auswertet und das Ergebnis ausgibt.

### Anforderungen

- Ganzzahlen und Dezimalzahlen (`3`, `3.14`)
- Operatoren `+`, `-`, `*`, `/`
- Klammerung `( ... )`
- Korrekte **Operatorrangfolge** (`*`/`/` vor `+`/`-`)
- Eingaben werden mit `;` abgeschlossen
- Mehrere Ausdrücke hintereinander sind erlaubt; jedes Ergebnis wird in einer eigenen Zeile ausgegeben

---

# Teil 2 – Rechner mit Variablen

## Aufgabe

Erweitern Sie den Rechner aus Teil 1 um **Variablen**.

### Anforderungen

- Zuweisungen der Form `name = ausdruck;`
- Variablen können in nachfolgenden Ausdrücken verwendet werden
- Bezeichner: Buchstabe, gefolgt von beliebig vielen Buchstaben/Ziffern/Unterstrichen
- Bei Verwendung einer **undefinierten** Variable: aussagekräftige Fehlermeldung
- Zuweisungen erzeugen **keine** Ausgabe; nur reine Ausdrücke geben ihr Ergebnis aus
  ˚

### Hinweis zur Implementierung

Verwalten Sie Variablen in einem Python-`dict`, z. B.:

```python
variables = {}
# bei Zuweisung:
variables[name] = wert
# beim Lesen:
wert = variables[name]
```

# Teil 3 – Rechner mit Funktionen

## Aufgabe

Erweitern Sie den Rechner aus Teil 2 um **benutzerdefinierte Funktionen**.

- Funktionsdefinition: `def name(p1, p2, ...) = ausdruck;`
- Funktionsaufruf: `name(arg1, arg2, ...)` als Bestandteil eines Ausdrucks
- Funktionsaufrufe dürfen **verschachtelt** werden: `mul(sum(x,y), sum(x,y))`
- Beim Aufruf werden formale Parameter durch die ausgewerteten Argumente ersetzt (lokaler Scope)
- Funktionen dürfen auf zuvor definierte globale Variablen zugreifen
