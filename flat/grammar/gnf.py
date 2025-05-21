"""Greibach Normal Form conversion module with guaranteed termination."""
from .grammar import Grammar
from . import convert_to_cnf
import itertools
from collections import deque
import re

def _tokenise(text, terminals, non_terminals):
    out = []
    i = 0
    # Sort nonterminals by length in reverse order to match longer ones first
    sorted_non_terminals = sorted(non_terminals, key=len, reverse=True)
    while i < len(text):
        matched = False
        for nt in sorted_non_terminals:
            if text.startswith(nt, i):
                out.append(nt)
                i += len(nt)
                matched = True
                break
        if not matched:
            if text[i] in terminals:
                out.append(text[i])
            i += 1
    return out

def convert_to_gnf(grammar):
    """
    Converts the given grammar (assumed to be in CNF) to Greibach Normal Form (GNF).
    Returns a new Grammar object in GNF.
    """
    grammar = convert_to_cnf(grammar)
    _aux_counter = itertools.count(1)

    def _new_nonterminal():
        return f"B{next(_aux_counter)}"

    def get_index(nt):
        # Extract number from X{number} or B{number} format
        match = re.match(r'[XB](\d+)', nt)
        return int(match.group(1)) if match else 0

    nonterms = sorted(list(grammar.non_terminals), key=get_index)
    prods = {nt: list(grammar.productions.get(nt, [])) for nt in nonterms}
    start_symbol = grammar.start_symbol
    terms = set(grammar.terminals)
    all_nts = set(nonterms)

    # Step 1: Process each nonterminal in order
    for i, Ai in enumerate(nonterms):
        # Step 1a: Replace Ai → Ajw with Ai → w'w where j < i
        for j in range(i):
            Aj = nonterms[j]
            updated_rules = []
            for rule in prods[Ai]:
                tokens = _tokenise(rule, terms, all_nts)
                if tokens and tokens[0] == Aj:
                    remainder = ''.join(tokens[1:])
                    for aj_rule in prods[Aj]:
                        if aj_rule == 'ε':
                            new_rule = remainder or 'ε'
                        else:
                            new_rule = aj_rule + remainder
                        updated_rules.append(new_rule)
                else:
                    updated_rules.append(rule)
            prods[Ai] = updated_rules

        # Step 1b: Handle left recursion
        left_recursive = []
        other_rules = []
        for rule in prods[Ai]:
            tokens = _tokenise(rule, terms, all_nts)
            if tokens and tokens[0] == Ai:
                left_recursive.append(''.join(tokens[1:]))
            else:
                other_rules.append(rule)

        if left_recursive:
            Bi = _new_nonterminal()
            all_nts.add(Bi)
            # Add Bi → αk | αkBi productions
            prods[Bi] = [alpha + Bi for alpha in left_recursive] + ['ε']
            # Replace Ai productions with Ai → βl | βlBi
            prods[Ai] = [beta + Bi for beta in other_rules]

    # Step 2: Replace remaining nonterminal productions (from n-1 downto 1)
    for i in range(len(nonterms)-2, -1, -1):
        Ai = nonterms[i]
        updated_rules = []
        for rule in prods[Ai]:
            tokens = _tokenise(rule, terms, all_nts)
            if not tokens:
                updated_rules.append('ε')
                continue

            if tokens[0] in terms:
                updated_rules.append(rule)
                continue

            # Replace Ai → Ajα with Ai → wα
            Aj = tokens[0]
            remainder = ''.join(tokens[1:])
            for aj_rule in prods[Aj]:
                if aj_rule == 'ε':
                    new_rule = remainder or 'ε'
                else:
                    new_rule = aj_rule + remainder
                updated_rules.append(new_rule)
        prods[Ai] = updated_rules

    # Step 3: Replace Bk → Aiα productions
    for nt in list(prods.keys()):
        if nt.startswith('B'):
            updated_rules = []
            for rule in prods[nt]:
                tokens = _tokenise(rule, terms, all_nts)
                if not tokens:
                    updated_rules.append('ε')
                    continue

                if tokens[0] in terms:
                    updated_rules.append(rule)
                    continue

                # Replace Bk → Aiα with Bk → wα
                Ai = tokens[0]
                remainder = ''.join(tokens[1:])
                for ai_rule in prods[Ai]:
                    if ai_rule == 'ε':
                        new_rule = remainder or 'ε'
                    else:
                        new_rule = ai_rule + remainder
                    updated_rules.append(new_rule)
            prods[nt] = updated_rules

    # Final cleanup to ensure GNF form
    final_productions = {}
    for nt in prods:
        normalized = []
        for rhs in prods[nt]:
            if rhs == 'ε':
                if nt == start_symbol:
                    normalized.append(rhs)
                continue
                
            tokens = _tokenise(rhs, terms, all_nts)
            if not tokens:
                if nt == start_symbol:
                    normalized.append('ε')
                continue
                
            if tokens[0] in terms:
                normalized.append(rhs)
            else:
                # Replace leading nonterminal with its productions
                for subrule in prods[tokens[0]]:
                    if subrule == 'ε':
                        new_rhs = ''.join(tokens[1:]) or 'ε'
                    else:
                        new_rhs = subrule + ''.join(tokens[1:])
                    normalized.append(new_rhs)
        if normalized:
            final_productions[nt] = normalized

    gnf_nonterms = set(final_productions.keys())
    if start_symbol not in gnf_nonterms:
        gnf_nonterms.add(start_symbol)
        final_productions[start_symbol] = ['ε']

    return Grammar(
        non_terminals=gnf_nonterms,
        terminals=terms,
        productions=final_productions,
        start_symbol=start_symbol
    ).remove_unreachable_symbols()


def is_in_gnf(grammar):
    """
    Check if a grammar is in Greibach Normal Form.
    A non-start production must begin with a terminal.
    The start production may be ε or begin with a terminal.
    All trailing symbols after the first must be nonterminals.
    """
    for A, rhss in grammar.productions.items():
        for rhs in rhss:
            if rhs == 'ε':
                if A != grammar.start_symbol:
                    return False
            else:
                if rhs[0] not in grammar.terminals:
                    return False
                for sym in rhs[1:]:
                    if sym not in grammar.non_terminals:
                        return False
    return True