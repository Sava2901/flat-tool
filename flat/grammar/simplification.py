"""Grammar simplification module for FLAT-Tool.

This module provides functions to simplify context-free grammars by:
- Removing non-generating symbols
- Removing unreachable symbols
- Eliminating epsilon productions
- Eliminating unit productions
"""

from .grammar import Grammar

def remove_non_generating_symbols(grammar: Grammar) -> Grammar:
    """Remove non-generating symbols from a grammar.

    A non-generating symbol is a non-terminal that cannot derive any string of terminals.

    Args:
        grammar: The grammar to simplify.

    Returns:
        Grammar: A new grammar without non-generating symbols.
    """

    # TODO: Refactor the code - this has vibe coded as a bandaid fix

    # Set of generating non-terminals
    generating = set()

    # Iteratively find non-terminals that generate terminal strings
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.productions.items():
            if nt in generating:
                continue  # Already known to be generating

            for prod in productions:
                if all(symbol in grammar.terminals or symbol in generating or symbol == "ε" for symbol in prod):
                    generating.add(nt)
                    changed = True
                    break

    # Filter out non-generating non-terminals
    new_non_terminals = {nt for nt in grammar.non_terminals if nt in generating}

    # Filter out productions with non-generating symbols
    new_productions = {}
    for nt in new_non_terminals:
        new_productions[nt] = []
        for prod in grammar.productions.get(nt, []):
            if all(symbol in grammar.terminals or symbol in generating or symbol == "ε" or symbol == "" for symbol in prod):
                new_productions[nt].append(prod)

    # Check if the start symbol is generating
    if grammar.start_symbol not in generating:
        raise ValueError("The start symbol is non-generating, resulting in an empty language")

    return Grammar(
        non_terminals=new_non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )

def remove_unreachable_symbols(grammar: Grammar) -> Grammar:
    """Remove unreachable symbols from a grammar.

    An unreachable symbol is a symbol that cannot be reached from the start symbol.

    Args:
        grammar: The grammar to simplify.

    Returns:
        Grammar: A new grammar without unreachable symbols.
    """
    from collections import deque

    reachable = set()
    queue = deque([grammar.start_symbol])

    while queue:
        current = queue.popleft()
        if current not in reachable:
            reachable.add(current)
            for production in grammar.productions.get(current, []):
                for symbol in production:
                    if symbol in grammar.non_terminals and symbol not in reachable:
                        queue.append(symbol)

    # Make sure the start symbol is always included (even if isolated)
    reachable.add(grammar.start_symbol)

    new_non_terminals = reachable

    # Filter productions to include only those with reachable LHS
    new_productions = {
        nt: prods
        for nt, prods in grammar.productions.items()
        if nt in reachable
    }

    # Collect terminals used in reachable productions
    new_terminals = set()
    for prods in new_productions.values():
        for prod in prods:
            for symbol in prod:
                if symbol in grammar.terminals:
                    new_terminals.add(symbol)

    # Handle case where no terminals appear in any reachable production
    if not new_terminals and any([] in prods for prods in new_productions.values()):
        # Preserve one terminal from original grammar to avoid constructor error
        if grammar.terminals:
            new_terminals.add(next(iter(grammar.terminals)))

    return Grammar(
        non_terminals=new_non_terminals,
        terminals=new_terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )

def inline_nonterminals_generating_only_terminals(grammar: Grammar) -> Grammar:
    """
    Replace non-terminals that produce only terminal strings by their productions
    in all other productions.

    Args:
        grammar: The input grammar.

    Returns:
        Grammar: A new grammar with inlined terminal-only nonterminals.
    """

    #TODO: Refactor the code - this has vibe coded as a bandaid fix
    # - when replacing the non-terminals a few more words that could not be formed before appear

    # Step 1: Find nonterminals that produce only terminals (or epsilon)
    terminal_only_nts = set()
    
    for nt, prods in grammar.productions.items():
        # Check if all productions contain only terminals or epsilon
        all_terminal = True
        for prod in prods:
            if prod == "ε":
                continue
            for symbol in prod:
                if symbol in grammar.non_terminals:
                    all_terminal = False
                    break
            if not all_terminal:
                break
        
        if all_terminal and nt != grammar.start_symbol:
            terminal_only_nts.add(nt)

    # If no terminal-only nonterminals found, return original grammar
    if not terminal_only_nts:
        return grammar

    # Step 2: Create new productions by expanding terminal-only nonterminals
    new_productions = {}

    for nt, prods in grammar.productions.items():
        new_productions[nt] = []
        
        for prod in prods:
            if prod == "ε":
                new_productions[nt].append(prod)
                continue
                
            # Find all occurrences of terminal-only nonterminals in the production
            replacements = {}
            for terminal_nt in terminal_only_nts:
                indexes = []
                for i in range(len(prod)):
                    if prod[i:i+len(terminal_nt)] == terminal_nt:
                        indexes.append(i)
                if indexes:
                    replacements[terminal_nt] = indexes
            
            if not replacements:
                # No terminal-only nonterminals in this production
                new_productions[nt].append(prod)
                continue
                
            # Generate all possible combinations
            current_prods = [prod]
            for terminal_nt, positions in replacements.items():
                nt_replacements = [p for p in grammar.productions[terminal_nt] if p != "ε"]
                if "ε" in grammar.productions[terminal_nt]:
                    nt_replacements.append("")  # Empty string for epsilon
                    
                new_current_prods = []
                for current_prod in current_prods:
                    for pos in positions:
                        for replacement in nt_replacements:
                            new_prod = current_prod[:pos] + replacement + current_prod[pos+len(terminal_nt):]
                            new_current_prods.append(new_prod)
                
                if new_current_prods:
                    current_prods = new_current_prods
            
            # Add all generated productions
            for p in current_prods:
                if not p:
                    p = "ε"
                if p not in new_productions[nt]:
                    new_productions[nt].append(p)

    # Step 3: Remove terminal-only nonterminals from non_terminals, except start symbol
    new_non_terminals = grammar.non_terminals - terminal_only_nts
    if grammar.start_symbol in terminal_only_nts:
        new_non_terminals.add(grammar.start_symbol)

    return Grammar(
        non_terminals=new_non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )

def merge_nonterminals_with_same_productions(grammar: Grammar) -> Grammar:
    """
    Merge nonterminals that have exactly the same productions by renaming one into the other,
    removing duplicates, and preserving the start symbol.

    Args:
        grammar: The input grammar.

    Returns:
        Grammar: New grammar with merged equivalent nonterminals.
    """
    # Helper to normalize productions for comparison
    def normalize_prods(prods):
        # Convert each production (list of symbols) to tuple for hashing
        return frozenset(tuple(prod) for prod in prods)

    prod_map = {}    # normalized productions -> representative nonterminal
    rename_map = {}  # nonterminal to rename -> target nonterminal

    # Step 1: Find equivalent nonterminals
    for nt in grammar.non_terminals:
        prods = grammar.productions.get(nt, [])
        normalized = normalize_prods(prods)
        if normalized in prod_map:
            existing_nt = prod_map[normalized]

            # Preserve start symbol: never rename it away
            if nt == grammar.start_symbol:
                rename_map[existing_nt] = nt
                prod_map[normalized] = nt  # Update representative
            elif existing_nt == grammar.start_symbol:
                rename_map[nt] = existing_nt
            else:
                rename_map[nt] = existing_nt
        else:
            prod_map[normalized] = nt

    # Step 2: Build new productions with renaming
    new_productions = {}

    for nt, prods in grammar.productions.items():
        # Skip nonterminals that are renamed away and not the start symbol
        if nt in rename_map and nt != grammar.start_symbol:
            continue

        new_nt = rename_map.get(nt, nt)

        new_prods = []
        for prod in prods:
            # Rename symbols inside production if needed
            new_prod = [rename_map.get(sym, sym) if sym in grammar.non_terminals else sym for sym in prod]
            new_prods.append(new_prod)

        # Convert list of symbols to string productions, handle epsilon (empty production)
        new_prods_str = []
        for prod in new_prods:
            if len(prod) == 0:
                new_prods_str.append("ε")  # or use "" depending on your convention
            else:
                new_prods_str.append(''.join(prod))

        # Merge productions if already present
        if new_nt in new_productions:
            new_productions[new_nt].extend(new_prods_str)
        else:
            new_productions[new_nt] = new_prods_str

    # Step 3: Build new nonterminals set (remove renamed-away, keep start symbol)
    new_non_terminals = {
        nt for nt in grammar.non_terminals if nt not in rename_map or nt == grammar.start_symbol
    }

    return Grammar(
        non_terminals=new_non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )

def eliminate_epsilon_productions(grammar: Grammar) -> Grammar:
    """Eliminate epsilon productions from a grammar.

     An epsilon production is a production of the form A → ε.

     Args:
         grammar: The grammar to simplify.

     Returns:
         Grammar: A new grammar without epsilon productions.
    """

    if len(grammar.productions) == 1:
        return grammar

    nullable = set()

    # Step 1: Identify all nullable non-terminals
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.productions.items():
            if nt in nullable:
                continue
            for prod in productions:
                if prod == "ε" or all(symbol in nullable for symbol in prod):
                    nullable.add(nt)
                    changed = True
                    break

    # Step 2: Generate all possible combinations by removing nullable symbols
    new_productions = {nt: set() for nt in grammar.non_terminals}
    for nt in grammar.non_terminals:
        for prod in grammar.productions.get(nt, []):
            if prod == "ε":
                continue
            symbols = list(prod)
            positions = [i for i, sym in enumerate(symbols) if sym in nullable]
            n = len(positions)
            for mask in range(1 << n):
                temp = symbols[:]
                for j in range(n):
                    if mask & (1 << j):
                        temp[positions[j]] = None
                new_prod = ''.join(s for s in temp if s is not None)
                if new_prod:
                    new_productions[nt].add(new_prod)
            if isinstance(prod, list):
                for p in prod:
                    new_productions[nt].add(p)
            elif isinstance(prod, str):
                new_productions[nt].add(prod)

    # Step 3: Remove non-terminals with no productions left
    changed = True
    while changed:
        changed = False
        empty_nonterminals = [nt for nt, rules in new_productions.items() if not rules]
        for nt in empty_nonterminals:
            del new_productions[nt]
            changed = True
            for k in list(new_productions):
                filtered = {p for p in new_productions[k] if nt not in p}
                if filtered != new_productions[k]:
                    new_productions[k] = filtered

    # Step 4: Special case if start symbol is nullable
    if grammar.start_symbol in nullable:
        new_start = grammar.start_symbol + "'"
        while new_start in new_productions:
            new_start += "'"

        # If the original start symbol is no longer in any productions or has no productions
        if grammar.start_symbol not in new_productions or not new_productions[grammar.start_symbol]:
            # Only ε is derivable
            new_productions = {new_start: {"ε"}}
            return Grammar(
                non_terminals={new_start},
                terminals=grammar.terminals,
                productions={new_start: ["ε"]},
                start_symbol=new_start
            )
        else:
            # Retain both ε and start symbol path
            new_productions[new_start] = {grammar.start_symbol, "ε"}
            new_non_terminals = set(new_productions.keys()) | {new_start}
            return Grammar(
                non_terminals=new_non_terminals,
                terminals=grammar.terminals,
                productions={nt: list(rules) for nt, rules in new_productions.items()},
                start_symbol=new_start
            )

    return Grammar(
        non_terminals=set(new_productions.keys()),
        terminals=grammar.terminals,
        productions={nt: list(rules) for nt, rules in new_productions.items()},
        start_symbol=grammar.start_symbol
    )

def eliminate_unit_productions(grammar: Grammar) -> Grammar:
    """Eliminate unit productions from a grammar.
    
    A unit production is a production of the form A → B, where B is a non-terminal.
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A new grammar without unit productions.
    """

    # For each non-terminal, find all non-terminals it can derive through unit productions
    unit_pairs = {nt: {nt} for nt in grammar.non_terminals}
    
    changed = True
    while changed:
        changed = False
        for nt in grammar.non_terminals:
            for prod in grammar.productions.get(nt, []):
                # Check if this is a unit production
                if len(prod) == 1 and prod[0] in grammar.non_terminals:
                    # Add all unit pairs of the derived non-terminal
                    for derived in unit_pairs[prod]:
                        if derived not in unit_pairs[nt]:
                            unit_pairs[nt].add(derived)
                            changed = True
    
    # Create new productions by replacing unit productions
    new_productions = {nt: [] for nt in grammar.non_terminals}
    
    for nt in grammar.non_terminals:
        for derived in unit_pairs[nt]:
            for prod in grammar.productions.get(derived, []):
                # Skip unit productions
                if len(prod) == 1 and prod[0] in grammar.non_terminals:
                    continue
                    
                # Add the non-unit production
                if prod not in new_productions[nt]:
                    new_productions[nt].append(prod)
    
    return Grammar(
        non_terminals=grammar.non_terminals,
        terminals=grammar.terminals,
        productions=new_productions,
        start_symbol=grammar.start_symbol
    )

def simplify_grammar(grammar: Grammar) -> Grammar:
    """Apply all simplification steps to a grammar.
    
    This function applies the following simplifications in order:
    1. Remove non-generating symbols
    2. Remove unreachable symbols
    3. Eliminate epsilon productions
    4. Eliminate unit productions
    5. Remove any new non-generating or unreachable symbols
    
    Args:
        grammar: The grammar to simplify.
        
    Returns:
        Grammar: A simplified equivalent grammar.
    """
    
    grammar = eliminate_unit_productions(grammar)

    grammar = remove_unreachable_symbols(grammar)
    # grammar = inline_nonterminals_generating_only_terminals(grammar)
    grammar = merge_nonterminals_with_same_productions(grammar)
    # grammar = inline_nonterminals_generating_only_terminals(grammar)
    grammar = remove_unreachable_symbols(grammar)

    grammar = eliminate_epsilon_productions(grammar)

    grammar = eliminate_unit_productions(grammar)

    grammar = remove_unreachable_symbols(grammar)
    # grammar = inline_nonterminals_generating_only_terminals(grammar)
    grammar = merge_nonterminals_with_same_productions(grammar)
    # grammar = inline_nonterminals_generating_only_terminals(grammar)
    grammar = remove_unreachable_symbols(grammar)

    return grammar