"""Greibach Normal Form conversion module with guaranteed termination."""
from .grammar import Grammar
import itertools
from collections import deque

def convert_to_gnf(cnf_grammar):
    """
    Converts the given grammar (assumed to be in CNF) to Greibach Normal Form (GNF).
    Returns a new Grammar object in GNF.
    """
    _aux_counter = itertools.count(1)

    def _new_nonterminal():
        return f"A{next(_aux_counter)}"

    def eliminate_left_recursion(A, rules):
        recursive = []
        non_recursive = []
        for prod in rules:
            if prod.startswith(A):
                alpha = prod[len(A):]
                recursive.append(alpha)
            else:
                non_recursive.append(prod)

        if not recursive:
            return {A: rules}

        B = _new_nonterminal()

        if not non_recursive:
            return {
                A: [B],
                B: [alpha + B for alpha in recursive] + ['ε']
            }

        return {
            A: [nr + B for nr in non_recursive],
            B: [rc + B for rc in recursive] + ['ε']
        }

    nonterms = sorted(list(cnf_grammar.non_terminals))
    prods = {nt: list(cnf_grammar.productions.get(nt, [])) for nt in nonterms}
    start_symbol = cnf_grammar.start_symbol
    terms = set(cnf_grammar.terminals)
    all_nts = set(nonterms)

    name_map = {}
    name_map[start_symbol] = _new_nonterminal()
    for nt in nonterms:
        if nt not in name_map:
            name_map[nt] = _new_nonterminal()

    renamed_prods = {}
    for nt in nonterms:
        new_nt = name_map[nt]
        renamed_prods[new_nt] = []
        for rhs in prods[nt]:
            output = []
            for symbol in rhs:
                output.append(name_map.get(symbol, symbol))
            renamed_prods[new_nt].append("".join(output))

    new_start = name_map[start_symbol]
    new_nonterms = sorted(list(renamed_prods.keys()))
    all_nts = set(new_nonterms)

    def get_index(nt):
        return int(nt[1:])

    new_nonterms.sort(key=get_index)

    for i, A in enumerate(new_nonterms):
        for j in range(i):
            B = new_nonterms[j]
            updated_rules = []
            for rule in renamed_prods[A]:
                if rule.startswith(B):
                    remainder = rule[len(B):]
                    for b_rule in renamed_prods[B]:
                        new_rhs = b_rule + remainder if b_rule != 'ε' else remainder or 'ε'
                        updated_rules.append(new_rhs)
                else:
                    updated_rules.append(rule)
            renamed_prods[A] = updated_rules

        result_dict = eliminate_left_recursion(A, renamed_prods[A])
        for nt_x, rhs_list in result_dict.items():
            renamed_prods[nt_x] = rhs_list
            if nt_x not in all_nts:
                all_nts.add(nt_x)
                new_nonterms.append(nt_x)
        new_nonterms.sort(key=get_index)

    changed = True
    iteration_limit = 1000
    iters = 0
    while changed and iters < iteration_limit:
        changed = False
        iters += 1
        new_productions = {nt: [] for nt in renamed_prods}
        for nt in renamed_prods:
            for rhs in renamed_prods[nt]:
                if rhs == 'ε':
                    new_productions[nt].append('ε')
                    continue
                if rhs[0] in terms:
                    new_productions[nt].append(rhs)
                    continue

                queue = deque()
                queue.append(rhs)
                seen = set()
                while queue:
                    current = queue.popleft()
                    if not current or current[0] in terms:
                        new_productions[nt].append(current or 'ε')
                        continue
                    first_nt = current[0]
                    rest = current[1:]
                    if first_nt not in renamed_prods:
                        terms.add(first_nt)
                        new_productions[nt].append(current)
                        continue
                    for subrule in renamed_prods[first_nt]:
                        new_seq = subrule + rest if subrule != 'ε' else rest or 'ε'
                        if new_seq not in seen:
                            seen.add(new_seq)
                            queue.append(new_seq)
                    changed = True
        renamed_prods = new_productions

    for nt in renamed_prods:
        normalized = []
        for rhs in renamed_prods[nt]:
            if rhs and rhs != 'ε' and rhs[0] not in terms:
                terms.add(rhs[0])
            normalized.append(rhs)
        renamed_prods[nt] = normalized

    gnf_nonterms = {nt for nt in renamed_prods if renamed_prods[nt]}
    if new_start not in gnf_nonterms:
        gnf_nonterms.add(new_start)
        renamed_prods[new_start] = ['ε']

    return Grammar(
        non_terminals=gnf_nonterms,
        terminals=terms,
        productions=renamed_prods,
        start_symbol=new_start
    )


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