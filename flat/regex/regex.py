"""Regular Expression module for FLAT-Tool.

This module provides the RegularExpression class for representing and manipulating regular expressions.
"""

from typing import Dict, List, Set, Optional, Tuple, Union, Any
import re


class RegularExpression:
    """Class for representing and manipulating regular expressions.
    
    Regular expressions are patterns used to match character combinations in strings.
    In formal language theory, they define the Type 3 languages in the Chomsky hierarchy.
    
    Attributes:
        pattern (str): The regular expression pattern
        alphabet (Set[str]): Set of symbols used in the pattern
    """
    
    # Special symbols used in regular expressions
    EPSILON = 'ε'  # Empty string
    UNION = '|'    # Alternation/union
    CONCAT = '.'   # Concatenation (often implicit)
    STAR = '*'     # Kleene star (zero or more)
    PLUS = '+'     # One or more
    QMARK = '?'    # Zero or one
    LPAREN = '('   # Left parenthesis
    RPAREN = ')'   # Right parenthesis
    
    def __init__(self, pattern: str):
        """Initialize a RegularExpression instance.
        
        Args:
            pattern: The regular expression pattern
            
        Raises:
            ValueError: If the pattern is invalid
        """
        self.pattern = pattern
        self.alphabet = self._extract_alphabet()
        
        # Validate the pattern
        try:
            self._parse()
        except Exception as e:
            raise ValueError(f"Invalid regular expression pattern: {e}")
    
    def _extract_alphabet(self) -> Set[str]:
        """Extract the alphabet (set of symbols) from the pattern.
        
        Returns:
            Set[str]: The alphabet of the regular expression
        """
        # Remove all special symbols and extract individual characters
        special_chars = re.escape(self.UNION + self.STAR + self.PLUS + self.QMARK + self.LPAREN + self.RPAREN)
        return set(re.sub(f'[{special_chars}]', '', self.pattern))
    
    def _parse(self) -> Any:
        """Parse the regular expression pattern into a syntax tree.
        
        Returns:
            Any: The root node of the syntax tree
        """
        # TODO: Implement parsing algorithm for regular expressions
        # This would typically use a recursive descent parser or similar approach
        raise NotImplementedError("Regular expression parsing not implemented yet")
    
    def to_nfa(self) -> Any:  # Will return NFA type once circular imports are resolved
        """Convert the regular expression to an NFA using Thompson's construction algorithm.
        
        Returns:
            NFA: An NFA equivalent to this regular expression
        """
        # TODO: Implement Thompson's construction algorithm
        raise NotImplementedError("Conversion to NFA not implemented yet")
    
    def to_dfa(self) -> Any:  # Will return DFA type once circular imports are resolved
        """Convert the regular expression to a DFA.
        
        This is done by first converting to an NFA using Thompson's construction,
        then converting the NFA to a DFA using the subset construction algorithm.
        
        Returns:
            DFA: A DFA equivalent to this regular expression
        """
        nfa = self.to_nfa()
        return nfa.to_dfa()
    
    def matches(self, string: str) -> bool:
        """Check if the regular expression matches the given string.
        
        Args:
            string: The string to check
            
        Returns:
            bool: True if the regular expression matches the string, False otherwise
        """
        # Convert to NFA and check if it accepts the string
        nfa = self.to_nfa()
        return nfa.accepts(string)
    
    def union(self, other: 'RegularExpression') -> 'RegularExpression':
        """Compute the union of this regular expression with another one.
        
        The union of two regular expressions r and s is denoted as r|s and matches
        any string that is matched by either r or s.
        
        Args:
            other: Another regular expression
            
        Returns:
            RegularExpression: The union of the two regular expressions
        """
        return RegularExpression(f"({self.pattern}){self.UNION}({other.pattern})")
    
    def concatenate(self, other: 'RegularExpression') -> 'RegularExpression':
        """Compute the concatenation of this regular expression with another one.
        
        The concatenation of two regular expressions r and s is denoted as rs and matches
        any string that can be split into two parts, where the first part is matched by r
        and the second part is matched by s.
        
        Args:
            other: Another regular expression
            
        Returns:
            RegularExpression: The concatenation of the two regular expressions
        """
        return RegularExpression(f"({self.pattern})({other.pattern})")
    
    def star(self) -> 'RegularExpression':
        """Compute the Kleene star of this regular expression.
        
        The Kleene star of a regular expression r is denoted as r* and matches
        zero or more repetitions of strings matched by r.
        
        Returns:
            RegularExpression: The Kleene star of the regular expression
        """
        return RegularExpression(f"({self.pattern}){self.STAR}")
    
    def plus(self) -> 'RegularExpression':
        """Compute the plus of this regular expression.
        
        The plus of a regular expression r is denoted as r+ and matches
        one or more repetitions of strings matched by r.
        
        Returns:
            RegularExpression: The plus of the regular expression
        """
        return RegularExpression(f"({self.pattern}){self.PLUS}")
    
    def optional(self) -> 'RegularExpression':
        """Compute the optional of this regular expression.
        
        The optional of a regular expression r is denoted as r? and matches
        zero or one occurrence of a string matched by r.
        
        Returns:
            RegularExpression: The optional of the regular expression
        """
        return RegularExpression(f"({self.pattern}){self.QMARK}")
    
    def __str__(self) -> str:
        """Return a string representation of the regular expression."""
        return self.pattern
    
    def __repr__(self) -> str:
        """Return a string representation of the regular expression for debugging."""
        return f"RegularExpression('{self.pattern}')"