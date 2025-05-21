"""Grammar module for FLAT-Tool.

This module provides the base Grammar class for representing and manipulating formal grammars.
"""

from enum import Enum
from typing import Dict, List, Set

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
        # if not non_terminals:
        #     raise ValueError("Non-terminals set cannot be empty")
        # if not terminals:
        #     raise ValueError("Terminals set cannot be empty")
        # if not productions:
        #     raise ValueError("Productions dictionary cannot be empty")
        # if start_symbol not in non_terminals:
        #     raise ValueError(f"Start symbol '{start_symbol}' must be in non-terminals set")
        
        for nt in productions:
            for prod in productions[nt]:
                if prod == "":
                    raise ValueError(f"Empty string (\"\") is not allowed as a production for non-terminal '{nt}'. Use 'ε' for epsilon.")
        
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.terminals.add("ε")
        self.productions = productions
        self.start_symbol = start_symbol

    def __str__(self) -> str:
        """Return a detailed string representation of the grammar."""
        result = []

        result.append("Non-Terminals:")
        result.append(f"  {{ {', '.join(sorted(self.non_terminals))} }}")

        result.append("Terminals:")
        result.append(f"  {{ {', '.join(sorted(self.terminals))} }}")

        result.append("Productions:")
        for nt, prods in self.productions.items():
            formatted_prods = [' '.join(prod) if isinstance(prod, list) else prod for prod in prods]
            result.append(f"  {nt} -> {' | '.join(formatted_prods)}")

        result.append("Start Symbol:")
        result.append(f"  {self.start_symbol}\n")

        return "\n".join(result)

    def identify_type(self) -> GrammarType:
        """Identify the grammar type according to the Chomsky hierarchy.
        
        Returns:
            GrammarType: The identified grammar type
        """
        if self.is_regular():
            return GrammarType.TYPE_3
        
        if self.is_context_free():
            return GrammarType.TYPE_2
        
        if self.is_context_sensitive():
            return GrammarType.TYPE_1
        
        return GrammarType.TYPE_0

    def is_regular(self) -> bool:
        """Check if the grammar is regular (Type 3).

        A grammar is regular if all productions are:
        - ε
        - A → a
        - A → aB (right-linear) or A → Ba (left-linear), but not both in the same grammar

        Returns:
            bool: True if the grammar is regular, False otherwise
        """
        direction = None  # 'left' or 'right'

        for nt, prods in self.productions.items():
            for prod in prods:
                # Epsilon production
                if prod == 'ε':
                    continue
                # Non-terminal into terminal production
                if len(prod) == 1 and prod in self.terminals:
                    continue
                if len(prod) == 2:
                    # Right-linear
                    if prod[0] in self.terminals and prod[1] in self.non_terminals:
                        if direction is None:
                            direction = 'right'
                        elif direction != 'right':
                            return False
                        continue
                    # Left-linear
                    elif prod[1] in self.terminals and prod[0] in self.non_terminals:
                        if direction is None:
                            direction = 'left'
                        elif direction != 'left':
                            return False
                        continue
                return False  # Invalid production

        return True

    def is_context_free(self) -> bool:
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
    
    def is_context_sensitive(self) -> bool:
        """Check if the grammar is context-sensitive (Type 1).
        
        A grammar is context-sensitive if all productions are of the form:
        - αAβ → αγβ
        
        Where A is a non-terminal, α and β are strings of terminals and non-terminals,
        and γ is a non-empty string of terminals and non-terminals.
        
        Additionally, S → ε (epsilon) is allowed if S does not appear on the right side of any production.
        
        Returns:
            bool: True if the grammar is context-sensitive, False otherwise
        """

        # Flag if epsilon production S -> ε is present
        epsilon_production = False

        # 1) Check epsilon productions and empty strings
        for nt, prods in self.productions.items():
            if "ε" in prods:
                # Only allowed if nt is start_symbol
                if nt != self.start_symbol:
                    return False
                epsilon_production = True

        # 2) If epsilon production exists, check that start_symbol does NOT appear on any RHS
        if epsilon_production:
            for prods in self.productions.values():
                for prod in prods:
                    if self.start_symbol in prod:
                        return False

        # 3) Check non-contracting: |RHS| >= |LHS| for all productions except S → ε handled above
        for lhs, prods in self.productions.items():
            for rhs in prods:
                if rhs == "ε":
                    continue  # skip S → ε handled above
                if len(rhs) < len(lhs):
                    return False

        return True

    
    def has_epsilon_productions(self) -> bool:
        """Check if the grammar has epsilon (empty) productions.
        
        Returns:
            bool: True if the grammar has epsilon productions, False otherwise
        """
        for prods in self.productions.values():
            if 'ε' in prods:
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
        from .simplification import eliminate_epsilon_productions
        return eliminate_epsilon_productions(self)
    
    def eliminate_unit_productions(self) -> 'Grammar':
        """Eliminate unit productions from the grammar.
        
        Returns:
            Grammar: A new grammar without unit productions
        """
        from .simplification import eliminate_unit_productions
        return eliminate_unit_productions(self)
    
    def remove_unreachable_symbols(self) -> 'Grammar':
        """Remove unreachable symbols from the grammar.
        
        Returns:
            Grammar: A new grammar without unreachable symbols
        """
        from .simplification import remove_unreachable_symbols
        return remove_unreachable_symbols(self)
    
    def remove_non_generating_symbols(self) -> 'Grammar':
        """Remove non-generating symbols from the grammar.
        
        Returns:
            Grammar: A new grammar without non-generating symbols
        """
        from .simplification import remove_non_generating_symbols
        return remove_non_generating_symbols(self)
    
    def simplify(self) -> 'Grammar':
        """Simplify the grammar by removing unreachable and non-generating symbols.
        
        Returns:
            Grammar: A simplified grammar
        """
        from .simplification import simplify_grammar
        return simplify_grammar(self)
    
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
        from .cnf import convert_to_cnf
        return convert_to_cnf(self)
    
    def to_gnf(self) -> 'Grammar':
        """Convert the grammar to Greibach Normal Form (GNF).
        
        A grammar is in GNF if all productions are of the form:
        - A → aα
        
        Where A is a non-terminal, a is a terminal, and α is a (possibly empty) string of non-terminals.
        
        Returns:
            Grammar: A new grammar in Greibach Normal Form
        """
        from .gnf import convert_to_gnf
        return convert_to_gnf(self)