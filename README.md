# FLAT-Tool: Formal Languages and Automata Theory Toolkit

A comprehensive Python toolkit for working with formal languages, grammars, and automata theory concepts.

## Features

- Grammar Operations:
  - Identifying grammar type (Type 0 to Type 3) based on production rules
  - Eliminating epsilon and unit productions
  - Simplifying context-free grammars (removing unreachable/non-generating symbols)
  - Converting grammars to Chomsky Normal Form (CNF) and Greibach Normal Form (GNF)

- Automata Operations:
  - Generating equivalent Finite Automata (FA) for regular expressions
  - Supporting transformations between NFA, DFA, and regular expressions
  - Automata minimization and equivalence checking

- Regular Expression Operations:
  - Parsing and validating regular expressions
  - Converting between regular expressions and automata

## Project Structure

```
flat-tool/
├── flat/                      # Main package
│   ├── __init__.py
│   ├── grammar/               # Grammar-related modules
│   │   ├── __init__.py
│   │   ├── grammar.py         # Base grammar class
│   │   ├── grammar_type.py    # Grammar type identification
│   │   ├── simplification.py  # Grammar simplification operations
│   │   ├── cnf.py             # Chomsky Normal Form conversion
│   │   └── gnf.py             # Greibach Normal Form conversion
│   ├── automata/              # Automata-related modules
│   │   ├── __init__.py
│   │   ├── fa.py              # Finite Automata base class
│   │   ├── nfa.py             # Non-deterministic Finite Automata
│   │   ├── dfa.py             # Deterministic Finite Automata
│   │   └── transformations.py # Automata transformations
│   ├── regex/                 # Regular expression modules
│   │   ├── __init__.py
│   │   ├── regex.py           # Regular expression parsing and operations
│   │   └── conversions.py     # Regex to automata conversions
│   └── io/                    # Input/Output handling
│       ├── __init__.py
│       ├── parsers.py         # Input parsers (JSON, BNF, text)
│       └── formatters.py      # Output formatters
├── cli/                       # Command-line interface
│   ├── __init__.py
│   └── main.py                # CLI entry point
├── gui/                       # Optional GUI interface
│   ├── __init__.py
│   └── app.py                 # GUI application
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_grammar.py
│   ├── test_automata.py
│   └── test_regex.py
├── examples/                  # Example usage
│   ├── grammar_examples.py
│   ├── automata_examples.py
│   └── regex_examples.py
├── docs/                      # Documentation
├── requirements.txt           # Project dependencies
├── setup.py                   # Package setup script
└── README.md                  # Project documentation
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/flat-tool.git
cd flat-tool

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Run the CLI tool
python -m flat.cli.main --help
```

### Python API

#### Grammar Operations

```python
# Example: Grammar type identification
from flat.grammar import Grammar, identify_grammar_type
from flat.io import parse_bnf

# Parse grammar from string in BNF notation
grammar_str = """
S -> aS | bA
A -> aA | b
"""
grammar = parse_bnf(grammar_str)

# Identify grammar type
grammar_type = identify_grammar_type(grammar)
print(f"Grammar type: {grammar_type}")  # Output: Grammar type: Type 3 (Regular)

# Convert to Chomsky Normal Form
from flat.grammar import convert_to_cnf
cnf_grammar = convert_to_cnf(grammar)
print(cnf_grammar)
```

#### Automata Operations

```python
# Example: NFA to DFA conversion
from flat.automata import NFA, nfa_to_dfa

# Create an NFA
nfa = NFA(
    states={"q0", "q1", "q2"},
    alphabet={"a", "b"},
    transitions={
        "q0": {"a": {"q0", "q1"}, "ε": {"q1"}},
        "q1": {"b": {"q2"}},
        "q2": {}
    },
    initial_state="q0",
    final_states={"q2"}
)

# Convert NFA to DFA
dfa = nfa_to_dfa(nfa)
print(dfa)
```

#### Regular Expression Operations

```python
# Example: Regular expression to NFA conversion
from flat.regex import RegularExpression, regex_to_nfa
from flat.automata import nfa_to_dfa

# Create a regular expression
regex = RegularExpression("a(b|c)*")

# Convert regex to NFA
nfa = regex_to_nfa(regex)

# Convert NFA to DFA
dfa = nfa_to_dfa(nfa)

# Check if a string is accepted
print(dfa.accepts("abc"))  # Output: True
print(dfa.accepts("ad"))   # Output: False
```

### Command-Line Interface

```bash
# Grammar operations
python -m cli.main type examples/grammar_example.bnf
python -m cli.main simplify examples/grammar_example.bnf --output-format json
python -m cli.main cnf examples/grammar_example.bnf --output-file examples/cnf_output.bnf
python -m cli.main gnf examples/grammar_example.bnf --output-file examples/gnf_output.bnf

# Automata operations
python -m cli.main nfa2dfa examples/nfa_example.json --output-file examples/dfa_output.json

# Regular expression operations
python -m cli.main regex2nfa "a(b|c)*" --output-file examples/regex_nfa_output.json
python -m cli.main dfa2regex examples/dfa_example.json
```

For more examples, see the [examples directory](examples/).

## Input Formats

The toolkit supports multiple input formats:

1. **BNF Notation** (Backus-Naur Form):
   ```
   S -> aS | bA
   A -> aA | b
   ```

2. **JSON Format**:
   ```json
   {
     "non_terminals": ["S", "A"],
     "terminals": ["a", "b"],
     "start_symbol": "S",
     "productions": {
       "S": ["aS", "bA"],
       "A": ["aA", "b"]
     }
   }
   ```

3. **Text File Format**:
   ```
   # Grammar definition
   non_terminals: S, A
   terminals: a, b
   start_symbol: S
   productions:
   S -> aS | bA
   A -> aA | b
   ```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.