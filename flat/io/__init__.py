"""Input/Output module for FLAT-Tool.

This module provides parsers and formatters for various input and output formats,
including BNF notation, JSON, and text files.
"""

from .parsers import parse_bnf, parse_json, parse_text
from .formatters import format_bnf, format_json, format_text