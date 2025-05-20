"""Non-deterministic Finite Automaton module for FLAT-Tool.

This module provides the NFA class for representing and manipulating non-deterministic finite automata.
"""

from typing import Dict, List, Set, Optional, Tuple, Union, Any
from .fa import FiniteAutomaton


class NFA(FiniteAutomaton):
    """Class for representing Non-deterministic Finite Automata (NFA).
    
    In an NFA, for each state and input symbol, the transition function can return
    a set of possible next states (including the empty set).
    
    Attributes:
        states (Set[str]): Set of states
        alphabet (Set[str]): Set of input symbols
        transitions (Dict[str, Dict[str, Set[str]]]): Transition function
        initial_state (str): The initial state
        final_states (Set[str]): Set of final states
        epsilon (str): Symbol representing epsilon transitions (default: 'ε')
    """
    
    def __init__(self, 
                 states: Set[str], 
                 alphabet: Set[str], 
                 transitions: Dict[str, Dict[str, Set[str]]], 
                 initial_state: str, 
                 final_states: Set[str],
                 epsilon: str = 'ε'):
        """Initialize an NFA instance.
        
        Args:
            states: Set of states
            alphabet: Set of input symbols
            transitions: Transition function as a nested dictionary
            initial_state: The initial state
            final_states: Set of final states
            epsilon: Symbol representing epsilon transitions
            
        Raises:
            ValueError: If the NFA definition is invalid
        """
        super().__init__(states, alphabet, initial_state, final_states)
        
        # Validate transitions
        for state in transitions:
            if state not in states:
                raise ValueError(f"Transition state '{state}' is not in states set")
            for symbol in transitions[state]:
                if symbol != epsilon and symbol not in alphabet:
                    raise ValueError(f"Transition symbol '{symbol}' is not in alphabet set")
                for next_state in transitions[state][symbol]:
                    if next_state not in states:
                        raise ValueError(f"Transition next state '{next_state}' is not in states set")
        
        self.transitions = transitions
        self.epsilon = epsilon
    
    def epsilon_closure(self, state_set: Set[str]) -> Set[str]:
        """Compute the epsilon closure of a set of states.
        
        The epsilon closure of a set of states S is the set of states that can be reached
        from any state in S by following zero or more epsilon transitions.
        
        Args:
            state_set: Set of states to compute the epsilon closure for
            
        Returns:
            Set[str]: The epsilon closure of the given set of states
        """
        closure = set(state_set)  # Start with the input states
        stack = list(state_set)   # States to process
        
        while stack:
            state = stack.pop()
            if state in self.transitions and self.epsilon in self.transitions[state]:
                for next_state in self.transitions[state][self.epsilon]:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        
        return closure
    
    def accepts(self, input_string: str) -> bool:
        """Check if the NFA accepts the given input string.
        
        Args:
            input_string: The input string to check
            
        Returns:
            bool: True if the NFA accepts the input string, False otherwise
        """
        # Start with the epsilon closure of the initial state
        current_states = self.epsilon_closure({self.initial_state})
        
        # Process each input symbol
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False  # Invalid input symbol
            
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    next_states.update(self.transitions[state][symbol])
            
            # Compute epsilon closure of next states
            current_states = self.epsilon_closure(next_states)
            
            if not current_states:
                return False  # No valid transitions
        
        # Check if any current state is a final state
        return bool(current_states.intersection(self.final_states))
    
    def to_dfa(self) -> 'DFA':
        """Convert the NFA to a DFA using the subset construction algorithm.
        
        Returns:
            DFA: A DFA equivalent to this NFA
        """
        from .dfa import DFA  # Import here to avoid circular imports
        
        # Start with the epsilon closure of the initial state
        initial_dfa_state = frozenset(self.epsilon_closure({self.initial_state}))
        dfa_states = {initial_dfa_state}
        dfa_final_states = set()
        dfa_transitions = {}
        
        # States to process
        unprocessed = [initial_dfa_state]
        
        while unprocessed:
            current_dfa_state = unprocessed.pop()
            current_dfa_state_str = str(sorted(current_dfa_state))  # Convert to string for DFA state name
            
            # Check if this DFA state contains any NFA final states
            if any(state in self.final_states for state in current_dfa_state):
                dfa_final_states.add(current_dfa_state_str)
            
            # Initialize transitions for this DFA state
            dfa_transitions[current_dfa_state_str] = {}
            
            # Process each input symbol
            for symbol in self.alphabet:
                next_nfa_states = set()
                
                # Compute next NFA states for each NFA state in the current DFA state
                for nfa_state in current_dfa_state:
                    if nfa_state in self.transitions and symbol in self.transitions[nfa_state]:
                        next_nfa_states.update(self.transitions[nfa_state][symbol])
                
                # Compute epsilon closure of next NFA states
                next_dfa_state = frozenset(self.epsilon_closure(next_nfa_states))
                
                if next_dfa_state:
                    next_dfa_state_str = str(sorted(next_dfa_state))
                    dfa_transitions[current_dfa_state_str][symbol] = next_dfa_state_str
                    
                    # Add to unprocessed if not seen before
                    if next_dfa_state not in dfa_states:
                        dfa_states.add(next_dfa_state)
                        unprocessed.append(next_dfa_state)
        
        # Convert frozenset states to strings for DFA
        dfa_states_str = {str(sorted(state)) for state in dfa_states}
        initial_dfa_state_str = str(sorted(initial_dfa_state))
        
        return DFA(
            states=dfa_states_str,
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            initial_state=initial_dfa_state_str,
            final_states=dfa_final_states
        )
    
    def __str__(self) -> str:
        """Return a string representation of the NFA."""
        result = [f"States: {', '.join(sorted(self.states))}",
                 f"Alphabet: {', '.join(sorted(self.alphabet))}",
                 f"Initial state: {self.initial_state}",
                 f"Final states: {', '.join(sorted(self.final_states))}",
                 "Transitions:"]
        
        for state in sorted(self.states):
            if state not in self.transitions:
                continue
            for symbol in sorted(self.transitions[state]):
                next_states = self.transitions[state][symbol]
                if next_states:
                    result.append(f"  δ({state}, {symbol}) = {{{', '.join(sorted(next_states))}}}")        
        return "\n".join(result)