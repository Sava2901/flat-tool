"""Greibach Normal Form conversion module for FLAT-Tool.

This module provides functions to convert context-free grammars to Greibach Normal Form (GNF).
A grammar is in GNF if all productions are of the form:
- A → aα (where a is a terminal and α is a string of non-terminals)
- S → ε (only if S is the start symbol)
"""

from typing import Dict, List, Set, Tuple
from copy import deepcopy

from .grammar import Grammar
from .simplification import simplify_grammar
from .cnf import convert_to_cnf


def convert_to_gnf(grammar: Grammar) -> Grammar:
    """Convert a context-free grammar to Greibach Normal Form.
    
    The conversion process follows these steps:
    1. Convert the grammar to Chomsky Normal Form
    2. Establish an ordering of non-terminals
    3. Eliminate left recursion
    4. Convert productions to start with a terminal
    
    Args:
        grammar: The grammar to convert.
        
    Returns:
        Grammar: A new grammar in Greibach Normal Form.
    """
    # Step 1: Convert to CNF first
    grammar = convert_to_cnf(grammar)
    
    # Make a deep copy to avoid modifying the original grammar
    new_grammar = deepcopy(grammar)
    new_productions = deepcopy(grammar.productions)
    
    # Step 2: Establish an ordering of non-terminals
    ordered_non_terminals = list(grammar.non_terminals)
    # Ensure start symbol is first
    if grammar.start_symbol in ordered_non_terminals:
        ordered_non_terminals.remove(grammar.start_symbol)
        ordered_non_terminals.insert(0, grammar.start_symbol)
    
    # Step 3: Eliminate left recursion
    for i, A_i in enumerate(ordered_non_terminals):
        # Substitute earlier non-terminals in productions of A_i
        for j in range(i):
            A_j = ordered_non_terminals[j]
            new_A_i_productions = []
            
            for prod in new_productions[A_i]:
                if prod and prod[0] == A_j:
                    # Substitute A_j with its productions
                    for A_j_prod in new_productions[A_j]:
                        new_A_i_productions.append(A_j_prod + prod[1:])
                else:
                    new_A_i_productions.append(prod)
            
            new_productions[A_i] = new_A_i_productions
        
        # Eliminate immediate left recursion
        alpha_productions = []  # Productions not starting with A_i
        beta_productions = []   # Productions starting with A_i (without the A_i)
        
        for prod in new_productions[A_i]:
            if prod and prod[0] == A_i:
                beta_productions.append(prod[1:])
            else:
                alpha_productions.append(prod)
        
        if beta_productions:  # If there is left recursion
            # Create a new non-terminal
            new_nt = f"{A_i}'"
            while new_nt in grammar.non_terminals:
                new_nt += "'"
            
            # Update productions
            new_A_i_productions = []
            for alpha in alpha_productions:
                new_A_i_productions.append(alpha)
                if alpha:  # Skip empty productions
                    new_A_i_productions.append(alpha + new_nt)
            
            new_nt_productions = []
            for beta in beta_productions:
                if beta:  # Skip empty productions
                    new_nt_productions.append(beta)
                    new_nt_productions.append(beta + new_nt)
            
            # Update the grammar
            new_productions[A_i] = new_A_i_productions
            new_productions[new_nt] = new_nt_productions
            new_grammar.non_terminals.add(new_nt)
    
    # Step 4: Convert productions to start with a terminal
    for nt in new_grammar.non_terminals:
        new_nt_productions = []
        for prod in new_productions[nt]:
            if not prod:  # Skip empty productions
                new_nt_productions.append(prod)
                continue
                
            if prod[0] in grammar.terminals:
                # Already starts with a terminal
                new_nt_productions.append(prod)
            elif prod[0] in grammar.non_terminals:
                # Substitute the non-terminal with its productions
                for sub_prod in new_productions[prod[0]]:
                    if sub_prod:  # Skip empty productions
                        new_nt_productions.append(sub_prod + prod[1:])
        
        new_productions[nt] = new_nt_productions
    
    return Grammar(
        non_terminals=new_grammar.non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
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