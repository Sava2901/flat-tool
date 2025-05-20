"""Formatters for FLAT-Tool output formats.

This module provides functions to format Grammar objects into different output formats:
- BNF notation
- JSON format
- Text file format
"""

import json
from typing import Dict, List, Set, Union

from ..grammar.grammar import Grammar


def format_bnf(grammar: Grammar) -> str:
    """Format a Grammar object into BNF notation.
    
    Args:
        grammar: Grammar object to format.
    
    Returns:
        String containing the grammar in BNF notation.
    """
    result = []
    
    # Format each production rule
    for nt, productions in grammar.productions.items():
        rhs = " | ".join(productions)
        result.append(f"{nt} -> {rhs}")
    
    return "\n".join(result)


def format_json(grammar: Grammar) -> str:
    """Format a Grammar object into JSON format.
    
    Args:
        grammar: Grammar object to format.
    
    Returns:
        String containing the grammar in JSON format.
    """
    # Convert sets to lists for JSON serialization
    data = {
        "non_terminals": list(grammar.non_terminals),
        "terminals": list(grammar.terminals),
        "start_symbol": grammar.start_symbol,
        "productions": grammar.productions
    }
    
    return json.dumps(data, indent=2)


def format_text(grammar: Grammar) -> str:
    """Format a Grammar object into text file format.
    
    Args:
        grammar: Grammar object to format.
    
    Returns:
        String containing the grammar in text format.
    """
    result = ["# Grammar definition"]
    
    # Format non-terminals
    non_terminals_str = ", ".join(sorted(grammar.non_terminals))
    result.append(f"non_terminals: {non_terminals_str}")
    
    # Format terminals
    terminals_str = ", ".join(sorted(grammar.terminals))
    result.append(f"terminals: {terminals_str}")
    
    # Format start symbol
    result.append(f"start_symbol: {grammar.start_symbol}")
    
    # Format productions
    result.append("productions:")
    for nt, productions in grammar.productions.items():
        rhs = " | ".join(productions)
        result.append(f"{nt} -> {rhs}")
    
    return "\n".join(result)