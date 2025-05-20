"""Finite Automaton module for FLAT-Tool.

This module provides the base FiniteAutomaton class for representing and manipulating finite automata.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Set, Optional, Tuple, Union, Any


class FiniteAutomaton(ABC):
    """Abstract base class for finite automata.
    
    A finite automaton is defined as a 5-tuple M = (Q, Σ, δ, q0, F) where:
    - Q is a finite set of states
    - Σ is a finite set of input symbols (alphabet)
    - δ is the transition function
    - q0 is the initial state
    - F is the set of final (accepting) states
    
    Attributes:
        states (Set[str]): Set of states
        alphabet (Set[str]): Set of input symbols
        initial_state (str): The initial state
        final_states (Set[str]): Set of final states
    """
    
    def __init__(self, 
                 states: Set[str], 
                 alphabet: Set[str], 
                 initial_state: str, 
                 final_states: Set[str]):
        """Initialize a FiniteAutomaton instance.
        
        Args:
            states: Set of states
            alphabet: Set of input symbols
            initial_state: The initial state
            final_states: Set of final states
            
        Raises:
            ValueError: If the automaton definition is invalid
        """
        # Validate input
        if not states:
            raise ValueError("States set cannot be empty")
        if not alphabet:
            raise ValueError("Alphabet set cannot be empty")
        if initial_state not in states:
            raise ValueError(f"Initial state '{initial_state}' must be in states set")
        if not final_states.issubset(states):
            raise ValueError("Final states must be a subset of states")
        
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.final_states = final_states
    
    @abstractmethod
    def accepts(self, input_string: str) -> bool:
        """Check if the automaton accepts the given input string.
        
        Args:
            input_string: The input string to check
            
        Returns:
            bool: True if the automaton accepts the input string, False otherwise
        """
        pass
    
    @abstractmethod
    def to_dfa(self) -> 'DFA':
        """Convert the automaton to a DFA.
        
        Returns:
            DFA: A DFA equivalent to this automaton
        """
        pass
    
    def to_regex(self) -> str:
        """Convert the automaton to a regular expression.
        
        Returns:
            str: A regular expression equivalent to this automaton
        """
        # TODO: Implement conversion to regular expression
        raise NotImplementedError("Conversion to regular expression not implemented yet")
    
    def to_grammar(self) -> Any:  # Will return Grammar type once circular imports are resolved
        """Convert the automaton to a grammar.
        
        Returns:
            Grammar: A grammar equivalent to this automaton
        """
        # TODO: Implement conversion to grammar
        raise NotImplementedError("Conversion to grammar not implemented yet")
    
    def minimize(self) -> 'DFA':
        """Minimize the automaton.
        
        Returns:
            DFA: A minimized DFA equivalent to this automaton
        """
        # First convert to DFA if not already
        dfa = self.to_dfa()
        # TODO: Implement DFA minimization algorithm
        raise NotImplementedError("Automaton minimization not implemented yet")
    
    def is_equivalent(self, other: 'FiniteAutomaton') -> bool:
        """Check if this automaton is equivalent to another automaton.
        
        Two automata are equivalent if they accept the same language.
        
        Args:
            other: Another automaton to compare with
            
        Returns:
            bool: True if the automata are equivalent, False otherwise
        """
        # TODO: Implement automaton equivalence checking
        raise NotImplementedError("Automaton equivalence checking not implemented yet")
    
    def visualize(self) -> None:
        """Visualize the automaton using matplotlib and networkx."""
        # TODO: Implement automaton visualization
        raise NotImplementedError("Automaton visualization not implemented yet")