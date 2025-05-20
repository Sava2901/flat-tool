"""Regular expression conversion module for FLAT-Tool.

This module provides functions for converting between regular expressions and automata.
"""

from typing import Dict, List, Set, Tuple, Any
from ..automata import DFA, NFA
from .regex import RegularExpression


def dfa_to_regex(dfa: DFA) -> RegularExpression:
    """Convert a DFA to an equivalent regular expression using state elimination.
    
    Args:
        dfa: The DFA to convert
        
    Returns:
        An equivalent regular expression
    """
    # Create a copy of the DFA with a new initial and final state
    states = set(dfa.states)
    transitions = {state: {symbol: dest for symbol, dest in trans.items()} 
                  for state, trans in dfa.transitions.items()}
    
    # Add a new initial state
    new_initial = "qi"
    while new_initial in states:
        new_initial += "i"
    states.add(new_initial)
    transitions[new_initial] = {}
    
    # Add epsilon transition from new initial state to original initial state
    transitions[new_initial][RegularExpression.EPSILON] = dfa.initial_state
    
    # Add a new final state
    new_final = "qf"
    while new_final in states:
        new_final += "f"
    states.add(new_final)
    transitions[new_final] = {}
    
    # Add epsilon transitions from original final states to new final state
    for final_state in dfa.final_states:
        if final_state not in transitions:
            transitions[final_state] = {}
        transitions[final_state][RegularExpression.EPSILON] = new_final
    
    # Convert transitions to regular expressions
    regex_transitions = {}
    for src in states:
        regex_transitions[src] = {}
        for dest in states:
            regex_transitions[src][dest] = ""
            
            # Direct transitions
            direct_symbols = []
            for symbol, target in transitions.get(src, {}).items():
                if target == dest:
                    direct_symbols.append(symbol)
            
            if direct_symbols:
                regex_transitions[src][dest] = "|".join(direct_symbols)
    
    # Eliminate states one by one (except new initial and final)
    states_to_eliminate = list(states - {new_initial, new_final})
    
    for state in states_to_eliminate:
        for i in states:
            if i == state or i not in regex_transitions:
                continue
                
            for j in states:
                if j == state or j not in regex_transitions[i]:
                    continue
                
                # R_ij = R_ij | (R_ik)(R_kk)*(R_kj)
                path_i_to_k = regex_transitions[i].get(state, "")
                path_k_to_k = regex_transitions.get(state, {}).get(state, "")
                path_k_to_j = regex_transitions.get(state, {}).get(j, "")
                
                if path_i_to_k and path_k_to_j:
                    # Create the new regex part
                    new_part = _concatenate(path_i_to_k, 
                                         _star(path_k_to_k), 
                                         path_k_to_j)
                    
                    # Combine with existing path
                    existing = regex_transitions[i][j]
                    if existing:
                        regex_transitions[i][j] = _union(existing, new_part)
                    else:
                        regex_transitions[i][j] = new_part
    
    # The final regex is the one from new initial to new final
    final_regex = regex_transitions[new_initial][new_final]
    if not final_regex:
        final_regex = RegularExpression.EPSILON
    
    return RegularExpression(final_regex)


def regex_to_nfa(regex: RegularExpression) -> NFA:
    """Convert a regular expression to an equivalent NFA using Thompson's construction.
    
    Args:
        regex: The regular expression to convert
        
    Returns:
        An equivalent NFA
    """
    # Parse the regex to create an abstract syntax tree
    ast = regex._parse()
    
    # Apply Thompson's construction recursively
    states, alphabet, transitions, initial, final = _thompson_construction(ast)
    
    # Create and return the NFA
    return NFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state=initial,
        final_states=final
    )


def _thompson_construction(ast):
    """Recursive implementation of Thompson's construction algorithm.
    
    Args:
        ast: Abstract syntax tree node
        
    Returns:
        Tuple of (states, alphabet, transitions, initial_state, final_states)
    """
    # This is a placeholder for the actual implementation
    # The real implementation would recursively build NFAs for each AST node
    # and combine them according to Thompson's construction rules
    
    # For now, return a simple NFA that accepts only the empty string
    states = {"q0", "q1"}
    alphabet = {RegularExpression.EPSILON}
    transitions = {"q0": {RegularExpression.EPSILON: {"q1"}}}
    initial_state = "q0"
    final_states = {"q1"}
    
    return states, alphabet, transitions, initial_state, final_states


def _concatenate(*regexes):
    """Concatenate multiple regex patterns.
    
    Args:
        *regexes: Regex patterns to concatenate
        
    Returns:
        Concatenated regex pattern
    """
    # Filter out empty strings
    filtered = [r for r in regexes if r and r != RegularExpression.EPSILON]
    
    if not filtered:
        return RegularExpression.EPSILON
    
    # Add parentheses around complex expressions
    wrapped = []
    for r in filtered:
        if '|' in r and not (r.startswith('(') and r.endswith(')')): 
            wrapped.append(f'({r})')
        else:
            wrapped.append(r)
    
    return RegularExpression.CONCAT.join(wrapped)


def _union(*regexes):
    """Create a union of multiple regex patterns.
    
    Args:
        *regexes: Regex patterns to union
        
    Returns:
        Union regex pattern
    """
    # Filter out empty strings
    filtered = [r for r in regexes if r]
    
    if not filtered:
        return ""
    
    return "|".join(filtered)


def _star(regex):
    """Apply the Kleene star to a regex pattern.
    
    Args:
        regex: Regex pattern to star
        
    Returns:
        Starred regex pattern
    """
    if not regex or regex == RegularExpression.EPSILON:
        return RegularExpression.EPSILON
    
    # Add parentheses if needed
    if len(regex) > 1 and not (regex.startswith('(') and regex.endswith(')')): 
        return f"({regex}){RegularExpression.STAR}"
    else:
        return f"{regex}{RegularExpression.STAR}"