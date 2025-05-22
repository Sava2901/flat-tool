"""CYK (Cocke-Younger-Kasami) algorithm implementation for FLAT-Tool.

This module provides functions for checking if a word is in a grammar using the CYK algorithm
and visualizing the parsing table.
"""

from .grammar import Grammar
import re


def _tokenize_production(rhs, grammar):
    """Tokenize production rhs into non-terminals/terminals considering both sets."""
    if not rhs:
        return []

    symbols = sorted(
        list(grammar.non_terminals | grammar.terminals),
        key=len, 
        reverse=True
    )

    tokens = []
    i = 0
    while i < len(rhs):
        matched = False
        for s in symbols:
            if rhs[i:].startswith(s):
                tokens.append(s)
                i += len(s)
                matched = True
                break
        if not matched:
            raise ValueError(f"Invalid symbol in production: '{rhs[i:]}'")
    return tokens


def _tokenize(word, grammar):
    """Tokenize a word into terminals based on the grammar's terminal set.

    Args:
        word: The input word to tokenize (string of concatenated symbols)
        grammar: The grammar containing terminal definitions

    Returns:
        List[str]: List of tokenized terminals
    """
    if not word:
        return []
    if grammar is None or not hasattr(grammar, 'terminals'):
        return list(word)

    # Sort terminals by length (descending) to match longest first
    terminals = sorted([t for t in grammar.terminals if t != "ε"], key=len, reverse=True)

    tokens = []
    i = 0
    while i < len(word):
        matched = False
        for t in terminals:
            if word[i:].startswith(t):
                tokens.append(t)
                i += len(t)
                matched = True
                break
        if not matched:
            tokens.append(word[i])
            i += 1
    return tokens


def _format_cell(cell):
    """Format a cell's content for display.

    Args:
        cell: Set of non-terminals in the cell
    Returns:
        str: Formatted cell content
    """
    if not cell:
        return "∅"

    def sort_key(nt):
        m = re.match(r'([A-Za-z]+)(\d*)', nt)
        if m:
            base, num = m.groups()
            return (base, int(num) if num else 0)
        return (nt, 0)

    sorted_nts = sorted(cell, key=sort_key)
    return "{" + ",".join(sorted_nts) + "}"


def cyk_parse(grammar, word_tokens):
    """Run the CYK algorithm on a token list.

    Args:
        grammar: A grammar in CNF with productions: Dict[str, List[str]]
        word_tokens: List of terminals
    Returns:
        Tuple[bool, List[List[Set[str]]]]: membership flag and parse table
    """
    # Preprocess productions into lists of symbols
    prod_lists = {}  # X -> List[List[str]]
    for X, rhss in grammar.productions.items():
        prod_lists[X] = []
        for rhs in rhss:
            symbols = _tokenize_production(rhs, grammar)
            prod_lists[X].append(symbols)

    # Build binary index for quick lookup: (Y,Z) -> [X]
    binary_index = {}
    for X, lists in prod_lists.items():
        for symbols in lists:
            if len(symbols) == 2:
                key = tuple(symbols)
                binary_index.setdefault(key, []).append(X)

    n = len(word_tokens)
    # Initialize DP table V[i][j]
    V = [[set() for _ in range(n+1)] for _ in range(n+1)]

    # Base: substrings of length 1
    for i in range(1, n+1):
        t = word_tokens[i-1]
        for X, lists in prod_lists.items():
            for symbols in lists:
                if len(symbols) == 1 and symbols[0] == t:
                    V[i][i].add(X)

    # Build up for substrings length>=2
    for length in range(2, n+1):
        for i in range(1, n-length+2):
            j = i + length - 1
            for k in range(i, j):
                for Y in V[i][k]:
                    for Z in V[k+1][j]:
                        for X in binary_index.get((Y, Z), []):
                            V[i][j].add(X)

    return (grammar.start_symbol in V[1][n]), V


def format_parsing_table(V, tokens):
    """Return a string representation of the CYK parse table."""
    n = len(tokens)
    header = f"Word: {' '.join(tokens) if tokens else 'ε'}"
    # compute column widths
    widths = [max(len(_format_cell(V[i][j])) for i in range(1, j+1)) for j in range(1, n+1)]

    lines = [header]
    # header row
    line = '    ' + ''.join(f"{j:^{w+2}}" for j, w in enumerate(widths, 1))
    sep = '    ' + '-' * (sum(widths) + 2*n)
    lines.extend([line, sep])

    # each row
    for i in range(1, n+1):
        row = []
        for j in range(1, n+1):
            if i <= j:
                cell = _format_cell(V[i][j]).center(widths[j-1])
            else:
                cell = ' ' * widths[j-1]
            row.append(cell)
        lines.append(f"i={i} | " + ' '.join(row))
    return '\n'.join(lines)


def is_word_in_grammar(grammar, word, show_table=False):
    """Check membership using CYK (handles ε special-case)."""
    if not grammar.is_context_free():
        raise ValueError("Grammar must be context-free")
    from .cnf import is_in_cnf
    cnf_grammar = grammar if is_in_cnf(grammar) else grammar.to_cnf()

    # Handle empty word
    if word == "":
        if 'ε' in cnf_grammar.productions.get(cnf_grammar.start_symbol, []):
            return True
        return False

    tokens = _tokenize(word, cnf_grammar)
    in_lang, table = cyk_parse(cnf_grammar, tokens)
    if show_table:
        print(format_parsing_table(table, tokens))
    return in_lang