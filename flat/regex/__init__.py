"""Regular Expression module for FLAT-Tool.

This module provides classes and functions for working with regular expressions,
including parsing, validation, and conversion to automata.
"""

from .regex import RegularExpression
from .conversions import dfa_to_regex, regex_to_nfa