"""Automata conversion module for FLAT-Tool.

This module provides functions for converting between different types of automata
and regular expressions.
"""

from typing import Dict, List, Set, Tuple, Any
from collections import deque

from .nfa import NFA
from .dfa import DFA


def nfa_to_dfa(nfa: NFA) -> DFA:
    """Convert an NFA to an equivalent DFA using the subset construction algorithm.
    
    Args:
        nfa: The NFA to convert
        
    Returns:
        An equivalent DFA
    """
    # Get epsilon closure of initial state
    initial_closure = nfa.epsilon_closure({nfa.initial_state})
    initial_state_name = _set_to_state_name(initial_closure)
    
    # Initialize DFA components
    dfa_states = {initial_state_name}
    dfa_final_states = set()
    if any(state in nfa.final_states for state in initial_closure):
        dfa_final_states.add(initial_state_name)
    
    # Initialize transitions and worklist
    dfa_transitions = {}
    worklist = deque([initial_closure])
    processed_states = set()
    state_map = {initial_state_name: initial_closure}
    
    # Process all reachable state sets
    while worklist:
        current_state_set = worklist.popleft()
        current_state_name = _set_to_state_name(current_state_set)
        
        if current_state_name in processed_states:
            continue
        
        processed_states.add(current_state_name)
        dfa_transitions[current_state_name] = {}
        
        # For each symbol in the alphabet
        for symbol in nfa.alphabet:
            # Skip epsilon
            if symbol == nfa.epsilon:
                continue
                
            # Get next state set
            next_state_set = set()
            for state in current_state_set:
                if state in nfa.transitions and symbol in nfa.transitions[state]:
                    next_state_set.update(nfa.transitions[state][symbol])
            
            # Apply epsilon closure
            next_state_set = nfa.epsilon_closure(next_state_set)
            
            if not next_state_set:
                continue
                
            next_state_name = _set_to_state_name(next_state_set)
            
            # Add transition
            dfa_transitions[current_state_name][symbol] = next_state_name
            
            # Add to DFA states
            dfa_states.add(next_state_name)
            
            # Check if it's a final state
            if any(state in nfa.final_states for state in next_state_set):
                dfa_final_states.add(next_state_name)
            
            # Add to worklist if not processed
            if next_state_name not in processed_states:
                worklist.append(next_state_set)
                state_map[next_state_name] = next_state_set
    
    # Create DFA
    return DFA(
        states=dfa_states,
        alphabet=nfa.alphabet - {nfa.epsilon},
        transitions=dfa_transitions,
        initial_state=initial_state_name,
        final_states=dfa_final_states
    )


def _set_to_state_name(state_set: Set[str]) -> str:
    """Convert a set of states to a state name.
    
    Args:
        state_set: Set of state names
        
    Returns:
        A string representation of the state set
    """
    if not state_set:
        return "∅"  # Empty set
    return "{" + ",".join(sorted(state_set)) + "}"