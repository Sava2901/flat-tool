"""Greibach Normal Form conversion module for FLAT-Tool.

This module provides functions to convert context-free grammars to Greibach Normal Form (GNF).
A grammar is in GNF if all productions are of the form:
- A → aα (where a is a terminal and α is a string of non-terminals)
- S → ε (only if S is the start symbol)
"""

from .grammar import Grammar
from .cnf import convert_to_cnf


def convert_to_gnf(grammar: Grammar) -> Grammar:
    """
    Convert a grammar G in CNF to an equivalent grammar G' in GNF following the steps:

    1) Enumerate non-terminals: [A1, ..., An]
    2) For i=1 to n:
       - Replace productions Ai → Aj α with j < i by expanding Aj's productions
       - Factor left recursion for Ai by introducing new non-terminals
    3) For i=n-1 downto 1:
       - Replace Ai → Aj α with j > i by expanding Aj's productions
    4) Replace productions for newly introduced non-terminals similarly.

    Args:
        grammar: input grammar in CNF

    Returns:
        Grammar in GNF
    """


    return Grammar(
        non_terminals=set(non_terminals),
        terminals=terminals,
        productions=productions,
        start_symbol=start_symbol,
    )


def is_in_gnf(grammar: Grammar) -> bool:
    """Check if a grammar is in Greibach Normal Form.
    
    A grammar is in GNF if all productions are of the form:
    - A → aα (where a is a terminal and α is a string of non-terminals)
    - S → ε (only if S is the start symbol)
    
    Args:
        grammar: The grammar to check.
        
    Returns:
        bool: True if the grammar is in GNF, False otherwise.
    """
    for nt, productions in grammar.productions.items():
        for prod in productions:
            # Check for S → ε (allowed only if S is the start symbol)
            if prod == "ε" or prod == "":
                if nt != grammar.start_symbol:
                    return False
                continue
            
            # Check for A → aα (must start with a terminal)
            if not prod or prod[0] not in grammar.terminals:
                return False
            
            # Check that the rest of the production contains only non-terminals
            for symbol in prod[1:]:
                if symbol not in grammar.non_terminals:
                    return False
    
    return True