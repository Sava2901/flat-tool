"""Grammar type identification module for FLAT-Tool.

This module provides functions to identify the type of a grammar according to the Chomsky hierarchy.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Tuple

from .grammar import Grammar, GrammarType


def identify_grammar_type(grammar: Grammar) -> GrammarType:
    """Identify the type of a grammar according to the Chomsky hierarchy.
    
    Args:
        grammar: The grammar to identify.
        
    Returns:
        GrammarType: The identified grammar type (Type 0, 1, 2, or 3).
    """
    return grammar.identify_type()


def is_regular(grammar: Grammar) -> bool:
    """Check if the grammar is regular (Type 3).
    
    A grammar is regular if all production rules are of the form:
    - A → a (where A is a non-terminal and a is a terminal)
    - A → aB (where A and B are non-terminals and a is a terminal)
    - A → ε (where ε is the empty string)
    
    Args:
        grammar: The grammar to check.
        
    Returns:
        bool: True if the grammar is regular, False otherwise.
    """
    for nt, productions in grammar.productions.items():
        for prod in productions:
            # Check for A → ε
            if prod == "ε" or prod == "":
                continue
                
            # Check for A → a
            if len(prod) == 1 and prod in grammar.terminals:
                continue
                
            # Check for A → aB
            if len(prod) == 2:
                if prod[0] in grammar.terminals and prod[1] in grammar.non_terminals:
                    continue
            
            # If we get here, the production doesn't match any regular grammar pattern
            return False
    
    return True


def is_context_free(grammar: Grammar) -> bool:
    """Check if the grammar is context-free (Type 2).
    
    A grammar is context-free if all production rules are of the form:
    - A → α (where A is a non-terminal and α is a string of terminals and non-terminals)
    
    Args:
        grammar: The grammar to check.
        
    Returns:
        bool: True if the grammar is context-free, False otherwise.
    """
    for nt, productions in grammar.productions.items():
        # In a context-free grammar, the left-hand side must be a single non-terminal
        if nt not in grammar.non_terminals or len(nt) != 1:
            return False
    
    return True


def is_context_sensitive(grammar: Grammar) -> bool:
    """Check if the grammar is context-sensitive (Type 1).
    
    A grammar is context-sensitive if all production rules are of the form:
    - αAβ → αγβ (where A is a non-terminal, α and β are strings of terminals and non-terminals,
      and γ is a non-empty string of terminals and non-terminals)
    - S → ε (only if S is the start symbol and S does not appear on the right side of any rule)
    
    Args:
        grammar: The grammar to check.
        
    Returns:
        bool: True if the grammar is context-sensitive, False otherwise.
    """
    # Check for S → ε (allowed only if S is the start symbol and doesn't appear on the right side)
    epsilon_production = False
    for nt, productions in grammar.productions.items():
        if "ε" in productions or "" in productions:
            if nt != grammar.start_symbol:
                return False
            epsilon_production = True
    
    if epsilon_production:
        # Check that S doesn't appear on the right side of any rule
        for productions in grammar.productions.values():
            for prod in productions:
                if grammar.start_symbol in prod:
                    return False
    
    # Check that all other productions satisfy |α| ≤ |β| (non-contracting)
    for lhs, productions in grammar.productions.items():
        for rhs in productions:
            if rhs == "ε" or rhs == "":
                continue  # Already handled above
            
            # For context-sensitive grammars, the right-hand side should not be shorter
            # than the left-hand side (except for the S → ε rule)
            if len(rhs) < len(lhs):
                return False
    
    return True


def is_unrestricted(grammar: Grammar) -> bool:
    """Check if the grammar is unrestricted (Type 0).
    
    All grammars are Type 0 by definition, so this always returns True.
    This function is included for completeness.
    
    Args:
        grammar: The grammar to check.
        
    Returns:
        bool: Always True.
    """
    return True