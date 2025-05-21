"""Chomsky Normal Form conversion module for FLAT-Tool.

This module provides functions to convert context-free grammars to Chomsky Normal Form (CNF).
A grammar is in CNF if all productions are of the form:
- A → BC (where B and C are non-terminals)
- A → a (where a is a terminal)
- S → ε (only if S is the start symbol)
"""

import itertools

from .grammar import Grammar

def convert_to_cnf(grammar: Grammar) -> Grammar:
    """Convert a context-free grammar to Chomsky Normal Form.
    """

    def _replace(text, replacement_map):
        for key, value in replacement_map.items():
            text = text.replace(key, value)
        return text

    def _tokenise(text, terminals, non_terminals):
        out = []
        i = 0
        sorted_non_terminals = sorted(non_terminals, key=len, reverse=True)
        while i < len(text):
            matched = False
            for nt in sorted_non_terminals:
                if text.startswith(nt, i):
                    out.append(nt)
                    i += len(nt)
                    matched = True
                    break
            if not matched:
                if text[i] in terminals:
                    out.append(text[i])
                i += 1
        return out

    # Step 1: Simplify the grammar (remove ε-productions, unit productions, unreachable symbols)
    grammar = grammar.simplify()

    # Step 2: Rename all non-terminals to X{number} using exact string replacement
    rename_map = dict()
    counter = itertools.count(1)

    rename_map[grammar.start_symbol] = f"X{next(counter)}"

    for nt in sorted(grammar.non_terminals):
        if nt not in rename_map:
            rename_map[nt] = f"X{next(counter)}"

    new_start_symbol = rename_map[grammar.start_symbol]
    renamed_productions = dict()

    for lhs, rhs in grammar.productions.items():
        new_lhs = _replace(lhs, rename_map)
        new_rhs = [_replace(rep, rename_map) for rep in rhs]
        renamed_productions[new_lhs] = new_rhs

    grammar = Grammar(
        non_terminals=set(rename_map.values()),
        terminals=grammar.terminals,
        productions=dict(renamed_productions),
        start_symbol=new_start_symbol
    )

    # Step 3: Transform to CNF
    new_productions = dict()
    rename_map = dict()
    token_binaries = dict()

    for lhs, rhs in grammar.productions.items():
        for p in rhs:
            tokens = _tokenise(p, grammar.terminals, grammar.non_terminals)

            # Case: already CNF compliant
            if len(tokens) == 1 or (
                    len(tokens) == 2 and tokens[0] in grammar.non_terminals and tokens[1] in grammar.non_terminals):
                if lhs not in new_productions:
                    new_productions[lhs] = [p]
                else:
                    new_productions[lhs].append(p)
                continue

            # Replace terminals with new non-terminals
            for token in tokens:
                if token in grammar.terminals:
                    if token not in rename_map:
                        new_nt = f"X{next(counter)}"
                        grammar.non_terminals.add(new_nt)
                        rename_map[token] = new_nt
                        new_productions[new_nt] = [token]
            tokens = [_replace(token, rename_map) for token in tokens]

            # Collapse into CNF by creating binary rules
            while len(tokens) > 2:
                pair = ''.join(tokens[:2])
                if pair not in token_binaries:
                    new_nt = f"X{next(counter)}"
                    grammar.non_terminals.add(new_nt)
                    token_binaries[pair] = new_nt
                    new_productions[new_nt] = [tokens[0]+tokens[1]]
                tokens = [token_binaries[pair]] + tokens[2:]

            # Add final rule to new_productions
            if lhs not in new_productions:
                new_productions[lhs] = [''.join(tokens)]
            else:
                new_productions[lhs].append(''.join(tokens))

    grammar = Grammar(
        non_terminals=grammar.non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=new_start_symbol
    )

    return grammar

def is_in_cnf(grammar: Grammar) -> bool:
    """Check if a grammar is in Chomsky Normal Form.
    
    A grammar is in CNF if all productions are of the form:
    - A → BC (where B and C are non-terminals)
    - A → a (where a is a terminal)
    - S → ε (only if S is the start symbol)
    
    Args:
        grammar: The grammar to check.
        
    Returns:
        bool: True if the grammar is in CNF, False otherwise.
    """
    for nt, productions in grammar.productions.items():
        for prod in productions:
            # Check for S → ε (allowed only if S is the start symbol)
            if prod == "ε" or prod == "":
                if nt != grammar.start_symbol:
                    return False
                continue
            
            # Check for A → a (terminal production)
            if len(prod) == 1:
                if prod not in grammar.terminals:
                    return False
                continue
            
            # Check for A → BC (binary non-terminal production)
            if len(prod) == 2:
                if prod[0] not in grammar.non_terminals or prod[1] not in grammar.non_terminals:
                    return False
                continue
            
            # Any other production form is not in CNF
            return False
    
    return True