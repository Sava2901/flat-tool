"""Chomsky Normal Form conversion module for FLAT-Tool.

This module provides functions to convert context-free grammars to Chomsky Normal Form (CNF).
A grammar is in CNF if all productions are of the form:
- A → BC (where B and C are non-terminals)
- A → a (where a is a terminal)
- S → ε (only if S is the start symbol)
"""

from typing import Dict, List, Set, Tuple
from copy import deepcopy

from .grammar import Grammar
from .simplification import simplify_grammar


def convert_to_cnf(grammar: Grammar) -> Grammar:
    """Convert a context-free grammar to Chomsky Normal Form.
    
    The conversion process follows these steps:
    1. Simplify the grammar (remove non-generating symbols, unreachable symbols,
       epsilon productions, and unit productions)
    2. Convert terminal-mixed productions to use new non-terminals
    3. Convert long productions to binary productions
    
    Args:
        grammar: The grammar to convert.
        
    Returns:
        Grammar: A new grammar in Chomsky Normal Form.
    """
    # Step 1: Simplify the grammar
    grammar = simplify_grammar(grammar)
    
    # Make a deep copy to avoid modifying the original grammar
    new_grammar = deepcopy(grammar)
    new_non_terminals = set(grammar.non_terminals)
    new_productions = deepcopy(grammar.productions)
    
    # Step 2: Convert terminal-mixed productions
    terminal_map = {}  # Maps terminals to their corresponding non-terminals
    
    for nt, productions in grammar.productions.items():
        new_prods = []
        for prod in productions:
            # Skip productions that are already in CNF
            if len(prod) == 1 and prod in grammar.terminals:
                new_prods.append(prod)
                continue
                
            if len(prod) >= 2:
                new_prod = ""
                for symbol in prod:
                    if symbol in grammar.terminals:
                        # Create a new non-terminal for this terminal if needed
                        if symbol not in terminal_map:
                            new_nt = f"T_{symbol}"
                            while new_nt in new_non_terminals:
                                new_nt += "'"
                            terminal_map[symbol] = new_nt
                            new_non_terminals.add(new_nt)
                            new_productions[new_nt] = [symbol]
                        
                        # Use the new non-terminal instead of the terminal
                        new_prod += terminal_map[symbol]
                    else:
                        new_prod += symbol
                new_prods.append(new_prod)
            else:
                new_prods.append(prod)
        
        new_productions[nt] = new_prods
    
    # Step 3: Convert long productions to binary productions
    for nt, productions in list(new_productions.items()):
        new_prods = []
        for prod in productions:
            if len(prod) <= 2:
                new_prods.append(prod)
            else:
                # Create a series of new non-terminals for this long production
                current_nt = nt
                for i in range(len(prod) - 2):
                    next_symbol = prod[i]
                    rest = prod[i+1:]
                    
                    # Create a new non-terminal for the rest of the production
                    new_nt = f"{current_nt}_{i+1}"
                    while new_nt in new_non_terminals:
                        new_nt += "'"
                    
                    # Add the new non-terminal and its production
                    new_non_terminals.add(new_nt)
                    
                    # Add the binary production for the current non-terminal
                    if current_nt == nt and i == 0:
                        new_prods.append(next_symbol + new_nt)
                    else:
                        if current_nt not in new_productions:
                            new_productions[current_nt] = []
                        new_productions[current_nt].append(next_symbol + new_nt)
                    
                    current_nt = new_nt
                
                # Add the final binary production
                if current_nt not in new_productions:
                    new_productions[current_nt] = []
                new_productions[current_nt].append(prod[-2] + prod[-1])
        
        if nt in new_productions:  # Check if the key exists (it might have been removed)
            new_productions[nt] = new_prods
    
    return Grammar(
        non_terminals=new_non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )


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