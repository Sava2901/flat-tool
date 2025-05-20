"""Grammar module for FLAT-Tool.

This module provides the base Grammar class for representing and manipulating formal grammars.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Tuple, Union


class GrammarType(Enum):
    """Enumeration of grammar types according to the Chomsky hierarchy."""
    TYPE_0 = 0  # Unrestricted grammar
    TYPE_1 = 1  # Context-sensitive grammar
    TYPE_2 = 2  # Context-free grammar
    TYPE_3 = 3  # Regular grammar


class Grammar:
    """Base class for representing formal grammars.
    
    A formal grammar is defined as a 4-tuple G = (N, Σ, P, S) where:
    - N is a set of non-terminal symbols
    - Σ is a set of terminal symbols
    - P is a set of production rules
    - S is the start symbol
    
    Attributes:
        non_terminals (Set[str]): Set of non-terminal symbols
        terminals (Set[str]): Set of terminal symbols
        productions (Dict[str, List[str]]): Dictionary mapping non-terminals to their productions
        start_symbol (str): The start symbol of the grammar
    """
    
    def __init__(self, 
                 non_terminals: Set[str], 
                 terminals: Set[str], 
                 productions: Dict[str, List[str]], 
                 start_symbol: str):
        """Initialize a Grammar instance.
        
        Args:
            non_terminals: Set of non-terminal symbols
            terminals: Set of terminal symbols
            productions: Dictionary mapping non-terminals to their productions
            start_symbol: The start symbol of the grammar
            
        Raises:
            ValueError: If the grammar definition is invalid
        """
        # Validate input
        if not non_terminals:
            raise ValueError("Non-terminals set cannot be empty")
        if not terminals:
            raise ValueError("Terminals set cannot be empty")
        if not productions:
            raise ValueError("Productions dictionary cannot be empty")
        if start_symbol not in non_terminals:
            raise ValueError(f"Start symbol '{start_symbol}' must be in non-terminals set")
        
        # Check that all production keys are non-terminals
        for nt in productions:
            if nt not in non_terminals:
                raise ValueError(f"Production key '{nt}' is not in non-terminals set")
        
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol
        
    def __str__(self) -> str:
        """Return a string representation of the grammar in BNF notation."""
        result = []
        for nt, prods in self.productions.items():
            result.append(f"{nt} -> {' | '.join(prods)}")
        return "\n".join(result)
    
    def identify_type(self) -> GrammarType:
        """Identify the grammar type according to the Chomsky hierarchy.
        
        Returns:
            GrammarType: The identified grammar type
        """
        # Check if it's a Type 3 grammar (Regular)
        if self._is_regular():
            return GrammarType.TYPE_3
        
        # Check if it's a Type 2 grammar (Context-free)
        if self._is_context_free():
            return GrammarType.TYPE_2
        
        # Check if it's a Type 1 grammar (Context-sensitive)
        if self._is_context_sensitive():
            return GrammarType.TYPE_1
        
        # If none of the above, it's a Type 0 grammar (Unrestricted)
        return GrammarType.TYPE_0
    
    def _is_regular(self) -> bool:
        """Check if the grammar is regular (Type 3).
        
        A grammar is regular if all productions are of the form:
        - A → a
        - A → aB
        - A → ε (epsilon)
        
        Where A, B are non-terminals and a is a terminal.
        
        Returns:
            bool: True if the grammar is regular, False otherwise
        """
        for nt, prods in self.productions.items():
            for prod in prods:
                # Empty production (epsilon) is allowed
                if not prod:
                    continue
                
                # Check if production is of the form A → a
                if len(prod) == 1 and prod in self.terminals:
                    continue
                
                # Check if production is of the form A → aB
                if (len(prod) == 2 and 
                    prod[0] in self.terminals and 
                    prod[1] in self.non_terminals):
                    continue
                
                # If we reach here, the production doesn't match any regular form
                return False
        
        return True
    
    def _is_context_free(self) -> bool:
        """Check if the grammar is context-free (Type 2).
        
        A grammar is context-free if all productions are of the form:
        - A → α
        
        Where A is a non-terminal and α is a string of terminals and non-terminals.
        
        Returns:
            bool: True if the grammar is context-free, False otherwise
        """
        for nt, prods in self.productions.items():
            # In a context-free grammar, the left side of each production must be a single non-terminal
            if len(nt) != 1 or nt not in self.non_terminals:
                return False
        
        return True
    
    def _is_context_sensitive(self) -> bool:
        """Check if the grammar is context-sensitive (Type 1).
        
        A grammar is context-sensitive if all productions are of the form:
        - αAβ → αγβ
        
        Where A is a non-terminal, α and β are strings of terminals and non-terminals,
        and γ is a non-empty string of terminals and non-terminals.
        
        Additionally, S → ε (epsilon) is allowed if S does not appear on the right side of any production.
        
        Returns:
            bool: True if the grammar is context-sensitive, False otherwise
        """
        for nt, prods in self.productions.items():
            for prod in prods:
                # Special case: S → ε is allowed if S doesn't appear on the right side of any production
                if nt == self.start_symbol and not prod:
                    # Check if S appears on the right side of any production
                    for right_prods in self.productions.values():
                        for right_prod in right_prods:
                            if self.start_symbol in right_prod:
                                return False
                    continue
                
                # For all other productions, the right side must not be shorter than the left side
                if len(prod) < len(nt):
                    return False
        
        return True
    
    def has_epsilon_productions(self) -> bool:
        """Check if the grammar has epsilon (empty) productions.
        
        Returns:
            bool: True if the grammar has epsilon productions, False otherwise
        """
        for prods in self.productions.values():
            if '' in prods or 'ε' in prods:
                return True
        return False
    
    def has_unit_productions(self) -> bool:
        """Check if the grammar has unit productions.
        
        A unit production is of the form A → B, where both A and B are non-terminals.
        
        Returns:
            bool: True if the grammar has unit productions, False otherwise
        """
        for nt, prods in self.productions.items():
            for prod in prods:
                if prod in self.non_terminals:
                    return True
        return False
    
    def eliminate_epsilon_productions(self) -> 'Grammar':
        """Eliminate epsilon productions from the grammar.
        
        Returns:
            Grammar: A new grammar without epsilon productions
        """
        # TODO: Implement epsilon production elimination algorithm
        raise NotImplementedError("Epsilon production elimination not implemented yet")
    
    def eliminate_unit_productions(self) -> 'Grammar':
        """Eliminate unit productions from the grammar.
        
        Returns:
            Grammar: A new grammar without unit productions
        """
        # TODO: Implement unit production elimination algorithm
        raise NotImplementedError("Unit production elimination not implemented yet")
    
    def remove_unreachable_symbols(self) -> 'Grammar':
        """Remove unreachable symbols from the grammar.
        
        Returns:
            Grammar: A new grammar without unreachable symbols
        """
        # TODO: Implement unreachable symbol removal algorithm
        raise NotImplementedError("Unreachable symbol removal not implemented yet")
    
    def remove_non_generating_symbols(self) -> 'Grammar':
        """Remove non-generating symbols from the grammar.
        
        Returns:
            Grammar: A new grammar without non-generating symbols
        """
        # TODO: Implement non-generating symbol removal algorithm
        raise NotImplementedError("Non-generating symbol removal not implemented yet")
    
    def simplify(self) -> 'Grammar':
        """Simplify the grammar by removing unreachable and non-generating symbols.
        
        Returns:
            Grammar: A simplified grammar
        """
        # First remove non-generating symbols
        grammar = self.remove_non_generating_symbols()
        # Then remove unreachable symbols
        return grammar.remove_unreachable_symbols()
    
    def to_cnf(self) -> 'Grammar':
        """Convert the grammar to Chomsky Normal Form (CNF).
        
        A grammar is in CNF if all productions are of the form:
        - A → BC
        - A → a
        - S → ε (only if S is the start symbol and doesn't appear on the right side of any production)
        
        Where A, B, C are non-terminals, a is a terminal, and S is the start symbol.
        
        Returns:
            Grammar: A new grammar in Chomsky Normal Form
        """
        # TODO: Implement CNF conversion algorithm
        raise NotImplementedError("CNF conversion not implemented yet")
    
    def to_gnf(self) -> 'Grammar':
        """Convert the grammar to Greibach Normal Form (GNF).
        
        A grammar is in GNF if all productions are of the form:
        - A → aα
        
        Where A is a non-terminal, a is a terminal, and α is a (possibly empty) string of non-terminals.
        
        Returns:
            Grammar: A new grammar in Greibach Normal Form
        """
        # TODO: Implement GNF conversion algorithm
        raise NotImplementedError("GNF conversion not implemented yet")