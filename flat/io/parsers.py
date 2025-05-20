"""Parsers for FLAT-Tool input formats.

This module provides functions to parse different input formats into Grammar objects:
- BNF notation
- JSON format
- Text file format
"""

import json
import re
from typing import Dict, List, Set, Tuple, Union

from ..grammar.grammar import Grammar


def parse_bnf(input_text: str) -> Grammar:
    """Parse a grammar in BNF notation.
    
    Args:
        input_text: String containing grammar in BNF notation.
            Example:
            S -> aS | bA
            A -> aA | b
    
    Returns:
        Grammar object representing the parsed grammar.
    """
    non_terminals = set()
    terminals = set()
    productions = {}
    start_symbol = None
    
    # Split the input into lines and process each production rule
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    
    for line in lines:
        # Skip comments or empty lines
        if not line or line.startswith('#'):
            continue
            
        # Parse the production rule
        if '->' in line:
            lhs, rhs = line.split('->', 1)
            lhs = lhs.strip()
            
            # Add non-terminal
            non_terminals.add(lhs)
            
            # Set start symbol if not already set
            if start_symbol is None:
                start_symbol = lhs
                
            # Process right-hand side alternatives
            alternatives = [alt.strip() for alt in rhs.split('|')]
            productions[lhs] = alternatives
            
            # Extract terminals
            for alt in alternatives:
                for char in alt:
                    if char.islower() or not char.isalpha():
                        if char != 'ε' and char != 'ε':  # Exclude epsilon
                            terminals.add(char)
    
    return Grammar(
        non_terminals=non_terminals,
        terminals=terminals,
        productions=productions,
        start_symbol=start_symbol
    )


def parse_json(input_json: str) -> Grammar:
    """Parse a grammar in JSON format.
    
    Args:
        input_json: String containing grammar in JSON format.
            Example:
            {
              "non_terminals": ["S", "A"],
              "terminals": ["a", "b"],
              "start_symbol": "S",
              "productions": {
                "S": ["aS", "bA"],
                "A": ["aA", "b"]
              }
            }
    
    Returns:
        Grammar object representing the parsed grammar.
    """
    try:
        data = json.loads(input_json)
        
        # Validate required fields
        required_fields = ['non_terminals', 'terminals', 'start_symbol', 'productions']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert lists to sets where appropriate
        non_terminals = set(data['non_terminals'])
        terminals = set(data['terminals'])
        start_symbol = data['start_symbol']
        productions = data['productions']
        
        # Validate start symbol is in non-terminals
        if start_symbol not in non_terminals:
            raise ValueError(f"Start symbol '{start_symbol}' not in non-terminals")
        
        # Validate production keys are in non-terminals
        for nt in productions.keys():
            if nt not in non_terminals:
                raise ValueError(f"Production non-terminal '{nt}' not in non-terminals")
        
        return Grammar(
            non_terminals=non_terminals,
            terminals=terminals,
            productions=productions,
            start_symbol=start_symbol
        )
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")


def parse_text(input_text: str) -> Grammar:
    """Parse a grammar in text file format.
    
    Args:
        input_text: String containing grammar in text format.
            Example:
            # Grammar definition
            non_terminals: S, A
            terminals: a, b
            start_symbol: S
            productions:
            S -> aS | bA
            A -> aA | b
    
    Returns:
        Grammar object representing the parsed grammar.
    """
    non_terminals = set()
    terminals = set()
    productions = {}
    start_symbol = None
    
    # Split the input into lines
    lines = [line.strip() for line in input_text.split('\n')]
    
    # Process section by section
    section = None
    production_lines = []
    
    for line in lines:
        # Skip comments or empty lines
        if not line or line.startswith('#'):
            continue
            
        # Check for section headers
        if line.lower().startswith('non_terminals:'):
            section = 'non_terminals'
            value = line[len('non_terminals:'):].strip()
            non_terminals = {nt.strip() for nt in value.split(',') if nt.strip()}
        elif line.lower().startswith('terminals:'):
            section = 'terminals'
            value = line[len('terminals:'):].strip()
            terminals = {t.strip() for t in value.split(',') if t.strip()}
        elif line.lower().startswith('start_symbol:'):
            section = 'start_symbol'
            start_symbol = line[len('start_symbol:'):].strip()
        elif line.lower().startswith('productions:'):
            section = 'productions'
        elif section == 'productions' and '->' in line:
            # This is a production rule
            production_lines.append(line)
    
    # Parse production rules (similar to BNF parsing)
    for line in production_lines:
        lhs, rhs = line.split('->', 1)
        lhs = lhs.strip()
        
        # Process right-hand side alternatives
        alternatives = [alt.strip() for alt in rhs.split('|')]
        productions[lhs] = alternatives
    
    # Validate that we have all required components
    if not non_terminals:
        raise ValueError("No non-terminals specified")
    if not terminals:
        raise ValueError("No terminals specified")
    if not start_symbol:
        raise ValueError("No start symbol specified")
    if not productions:
        raise ValueError("No productions specified")
    
    return Grammar(
        non_terminals=non_terminals,
        terminals=terminals,
        productions=productions,
        start_symbol=start_symbol
    )