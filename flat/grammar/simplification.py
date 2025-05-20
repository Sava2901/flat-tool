"""Grammar simplification module for FLAT-Tool.

This module provides functions to simplify context-free grammars by:
- Removing non-generating symbols
- Removing unreachable symbols
- Eliminating epsilon productions
- Eliminating unit productions
"""

from typing import Dict, List, Set, Tuple
from copy import deepcopy

from .grammar import Grammar


def remove_non_generating_symbols(grammar: Grammar) -> Grammar:
    """Remove non-generating symbols from a grammar.
    
    A non-generating symbol is a non-terminal that cannot derive any string of terminals.
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A new grammar without non-generating symbols.
    """
    # Make a deep copy to avoid modifying the original grammar
    new_grammar = deepcopy(grammar)
    
    # Initialize the set of generating symbols with all terminals
    generating = set(grammar.terminals)
    
    # Iteratively find non-terminals that generate terminal strings
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.productions.items():
            if nt in generating:
                continue  # Already known to be generating
                
            for prod in productions:
                # Check if all symbols in the production are generating
                if all(symbol in generating for symbol in prod):
                    generating.add(nt)
                    changed = True
                    break
    
    # Filter out non-generating non-terminals
    new_non_terminals = {nt for nt in grammar.non_terminals if nt in generating}
    
    # Filter out productions with non-generating symbols
    new_productions = {}
    for nt in new_non_terminals:
        new_productions[nt] = []
        for prod in grammar.productions.get(nt, []):
            # Keep only productions where all symbols are generating
            if all(symbol in generating or symbol == "ε" or symbol == "" for symbol in prod):
                new_productions[nt].append(prod)
    
    # Check if the start symbol is generating
    if grammar.start_symbol not in generating:
        raise ValueError("The start symbol is non-generating, resulting in an empty language")
    
    return Grammar(
        non_terminals=new_non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )


def remove_unreachable_symbols(grammar: Grammar) -> Grammar:
    """Remove unreachable symbols from a grammar.
    
    An unreachable symbol is a symbol that cannot be reached from the start symbol.
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A new grammar without unreachable symbols.
    """
    # Make a deep copy to avoid modifying the original grammar
    new_grammar = deepcopy(grammar)
    
    # Initialize the set of reachable symbols with the start symbol
    reachable = {grammar.start_symbol}
    
    # Iteratively find symbols reachable from the start symbol
    changed = True
    while changed:
        changed = False
        new_reachable = set(reachable)  # Copy to avoid modifying during iteration
        
        for nt in reachable:
            if nt not in grammar.productions:
                continue
                
            for prod in grammar.productions[nt]:
                for symbol in prod:
                    if symbol not in reachable and (symbol in grammar.non_terminals or symbol in grammar.terminals):
                        new_reachable.add(symbol)
                        changed = True
        
        reachable = new_reachable
    
    # Filter out unreachable non-terminals and terminals
    new_non_terminals = {nt for nt in grammar.non_terminals if nt in reachable}
    new_terminals = {t for t in grammar.terminals if t in reachable}
    
    # Filter out productions with unreachable symbols
    new_productions = {}
    for nt in new_non_terminals:
        new_productions[nt] = grammar.productions.get(nt, [])
    
    return Grammar(
        non_terminals=new_non_terminals,
        terminals=new_terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )


def eliminate_epsilon_productions(grammar: Grammar) -> Grammar:
    """Eliminate epsilon productions from a grammar.
    
    An epsilon production is a production of the form A → ε.
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A new grammar without epsilon productions.
    """
    # Make a deep copy to avoid modifying the original grammar
    new_grammar = deepcopy(grammar)
    
    # Find all nullable non-terminals (those that can derive ε)
    nullable = set()
    for nt, productions in grammar.productions.items():
        if "ε" in productions or "" in productions:
            nullable.add(nt)
    
    # Iteratively find all nullable non-terminals
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.productions.items():
            if nt in nullable:
                continue  # Already known to be nullable
                
            for prod in productions:
                # A production is nullable if all its symbols are nullable
                if all(symbol in nullable for symbol in prod):
                    nullable.add(nt)
                    changed = True
                    break
    
    # Create new productions by considering all combinations of nullable symbols
    new_productions = {nt: [] for nt in grammar.non_terminals}
    
    for nt, productions in grammar.productions.items():
        for prod in productions:
            if prod == "ε" or prod == "":
                continue  # Skip epsilon productions
                
            # Add the original production
            if prod not in new_productions[nt]:
                new_productions[nt].append(prod)
            
            # Generate all combinations by removing nullable symbols
            nullable_positions = [i for i, symbol in enumerate(prod) if symbol in nullable]
            
            # For each subset of nullable positions, create a new production
            for mask in range(1, 2 ** len(nullable_positions)):
                # Create a new production by removing symbols at selected positions
                new_prod = ""
                for i, symbol in enumerate(prod):
                    # Check if this position should be removed
                    position_index = nullable_positions.index(i) if i in nullable_positions else -1
                    if position_index == -1 or not (mask & (1 << position_index)):
                        new_prod += symbol
                
                # Add the new production if it's not empty and not already added
                if new_prod and new_prod not in new_productions[nt]:
                    new_productions[nt].append(new_prod)
    
    # Special case: if the start symbol is nullable, add a new start symbol
    if grammar.start_symbol in nullable:
        new_start = grammar.start_symbol + "'"
        while new_start in grammar.non_terminals:
            new_start += "'"
        
        new_non_terminals = set(grammar.non_terminals)
        new_non_terminals.add(new_start)
        
        new_productions[new_start] = [grammar.start_symbol, "ε"]
        
        return Grammar(
            non_terminals=new_non_terminals,
            terminals=grammar.terminals,
            productions=new_productions,
            start_symbol=new_start
        )
    
    return Grammar(
        non_terminals=grammar.non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )


def eliminate_unit_productions(grammar: Grammar) -> Grammar:
    """Eliminate unit productions from a grammar.
    
    A unit production is a production of the form A → B, where B is a non-terminal.
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A new grammar without unit productions.
    """
    # Make a deep copy to avoid modifying the original grammar
    new_grammar = deepcopy(grammar)
    
    # For each non-terminal, find all non-terminals it can derive through unit productions
    unit_pairs = {nt: {nt} for nt in grammar.non_terminals}
    
    changed = True
    while changed:
        changed = False
        for nt in grammar.non_terminals:
            for prod in grammar.productions.get(nt, []):
                # Check if this is a unit production
                if len(prod) == 1 and prod in grammar.non_terminals:
                    # Add all unit pairs of the derived non-terminal
                    for derived in unit_pairs[prod]:
                        if derived not in unit_pairs[nt]:
                            unit_pairs[nt].add(derived)
                            changed = True
    
    # Create new productions by replacing unit productions
    new_productions = {nt: [] for nt in grammar.non_terminals}
    
    for nt in grammar.non_terminals:
        for derived in unit_pairs[nt]:
            for prod in grammar.productions.get(derived, []):
                # Skip unit productions
                if len(prod) == 1 and prod in grammar.non_terminals:
                    continue
                    
                # Add the non-unit production
                if prod not in new_productions[nt]:
                    new_productions[nt].append(prod)
    
    return Grammar(
        non_terminals=grammar.non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )


def simplify_grammar(grammar: Grammar) -> Grammar:
    """Apply all simplification steps to a grammar.
    
    This function applies the following simplifications in order:
    1. Remove non-generating symbols
    2. Remove unreachable symbols
    3. Eliminate epsilon productions
    4. Eliminate unit productions
    5. Remove any new non-generating or unreachable symbols
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A simplified equivalent grammar.
    """
    # Step 1: Remove non-generating symbols
    grammar = remove_non_generating_symbols(grammar)
    
    # Step 2: Remove unreachable symbols
    grammar = remove_unreachable_symbols(grammar)
    
    # Step 3: Eliminate epsilon productions
    grammar = eliminate_epsilon_productions(grammar)
    
    # Step 4: Eliminate unit productions
    grammar = eliminate_unit_productions(grammar)
    
    # Step 5: Remove any new non-generating or unreachable symbols
    grammar = remove_non_generating_symbols(grammar)
    grammar = remove_unreachable_symbols(grammar)
    
    return grammar