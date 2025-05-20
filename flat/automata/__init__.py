"""Automata module for FLAT-Tool.

This module provides classes and functions for working with finite automata,
including NFA, DFA, and transformations between them.
"""

from .fa import FiniteAutomaton
from .nfa import NFA
from .dfa import DFA
from .conversions import nfa_to_dfa