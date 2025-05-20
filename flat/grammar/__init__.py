"""Grammar module for FLAT-Tool.

This module provides classes and functions for working with formal grammars,
including grammar type identification, simplification, and normal form conversions.
"""

from .grammar import Grammar, GrammarType
from .grammar_type import identify_grammar_type, is_regular, is_context_free, is_context_sensitive, is_unrestricted
from .simplification import simplify_grammar, remove_non_generating_symbols, remove_unreachable_symbols, eliminate_epsilon_productions, eliminate_unit_productions
from .cnf import convert_to_cnf, is_in_cnf
from .gnf import convert_to_gnf, is_in_gnf