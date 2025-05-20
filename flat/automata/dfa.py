"""Deterministic Finite Automaton module for FLAT-Tool.

This module provides the DFA class for representing and manipulating deterministic finite automata.
"""

from typing import Dict, List, Set, Optional, Tuple, Union, Any
from .fa import FiniteAutomaton


class DFA(FiniteAutomaton):
    """Class for representing Deterministic Finite Automata (DFA).
    
    In a DFA, for each state and input symbol, the transition function returns
    exactly one next state.
    
    Attributes:
        states (Set[str]): Set of states
        alphabet (Set[str]): Set of input symbols
        transitions (Dict[str, Dict[str, str]]): Transition function
        initial_state (str): The initial state
        final_states (Set[str]): Set of final states
    """
    
    def __init__(self, 
                 states: Set[str], 
                 alphabet: Set[str], 
                 transitions: Dict[str, Dict[str, str]], 
                 initial_state: str, 
                 final_states: Set[str]):
        """Initialize a DFA instance.
        
        Args:
            states: Set of states
            alphabet: Set of input symbols
            transitions: Transition function as a nested dictionary
            initial_state: The initial state
            final_states: Set of final states
            
        Raises:
            ValueError: If the DFA definition is invalid
        """
        super().__init__(states, alphabet, initial_state, final_states)
        
        # Validate transitions
        for state in states:
            if state not in transitions:
                raise ValueError(f"Missing transitions for state '{state}'")
            for symbol in alphabet:
                if symbol not in transitions[state]:
                    raise ValueError(f"Missing transition for state '{state}' and symbol '{symbol}'")
                if transitions[state][symbol] not in states:
                    raise ValueError(f"Transition to non-existent state '{transitions[state][symbol]}'")
        
        self.transitions = transitions
    
    def accepts(self, input_string: str) -> bool:
        """Check if the DFA accepts the given input string.
        
        Args:
            input_string: The input string to check
            
        Returns:
            bool: True if the DFA accepts the input string, False otherwise
        """
        current_state = self.initial_state
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False  # Invalid input symbol
            
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False  # No valid transition
            
            current_state = self.transitions[current_state][symbol]
        
        return current_state in self.final_states
    
    def to_dfa(self) -> 'DFA':
        """Convert the DFA to a DFA (identity operation).
        
        Returns:
            DFA: This DFA (self)
        """
        return self
    
    def to_nfa(self) -> Any:  # Will return NFA type once circular imports are resolved
        """Convert the DFA to an NFA.
        
        Returns:
            NFA: An NFA equivalent to this DFA
        """
        from .nfa import NFA  # Import here to avoid circular imports
        
        # A DFA is already an NFA, just need to convert the transition function format
        nfa_transitions = {}
        
        for state in self.transitions:
            nfa_transitions[state] = {}
            for symbol in self.transitions[state]:
                next_state = self.transitions[state][symbol]
                nfa_transitions[state][symbol] = {next_state}
        
        return NFA(
            states=self.states,
            alphabet=self.alphabet,
            transitions=nfa_transitions,
            initial_state=self.initial_state,
            final_states=self.final_states
        )
    
    def minimize(self) -> 'DFA':
        """Minimize the DFA using Hopcroft's algorithm.
        
        Returns:
            DFA: A minimized DFA equivalent to this DFA
        """
        # TODO: Implement Hopcroft's algorithm for DFA minimization
        raise NotImplementedError("DFA minimization not implemented yet")
    
    def complement(self) -> 'DFA':
        """Compute the complement of this DFA.
        
        The complement of a DFA accepts all strings that the original DFA rejects,
        and rejects all strings that the original DFA accepts.
        
        Returns:
            DFA: The complement of this DFA
        """
        # Complement is obtained by swapping final and non-final states
        complement_final_states = self.states - self.final_states
        
        return DFA(
            states=self.states,
            alphabet=self.alphabet,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=complement_final_states
        )
    
    def __str__(self) -> str:
        """Return a string representation of the DFA."""
        result = [f"States: {', '.join(sorted(self.states))}",
                 f"Alphabet: {', '.join(sorted(self.alphabet))}",
                 f"Initial state: {self.initial_state}",
                 f"Final states: {', '.join(sorted(self.final_states))}",
                 "Transitions:"]
        
        for state in sorted(self.states):
            for symbol in sorted(self.alphabet):
                next_state = self.transitions[state][symbol]
                result.append(f"  δ({state}, {symbol}) = {next_state}")        
        return "\n".join(result)