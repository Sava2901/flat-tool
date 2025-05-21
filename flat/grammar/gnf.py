"""Greibach Normal Form conversion module with guaranteed termination."""
from .grammar import Grammar
import itertools
from collections import deque

def _tokenise(text, terminals, non_terminals):
    out = []
    i = 0
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
                
                tokens = _tokenise(rhs, terms, all_nts)
                if not tokens:
                    new_productions[nt].append('ε')
                    continue
                
                if tokens[0] in terms:
                    new_productions[nt].append(rhs)
                    continue

                queue = deque()
                queue.append(tokens)
                seen = set()
                while queue:
                    current_tokens = queue.popleft()
                    if not current_tokens:
                        new_productions[nt].append('ε')
                        continue
                    
                    first_token = current_tokens[0]
                    rest_tokens = current_tokens[1:]
                    
                    if first_token in terms:
                        new_productions[nt].append(''.join(current_tokens))
                        continue
                        
                    if first_token not in renamed_prods:
                        continue
                        
                    for subrule in renamed_prods[first_token]:
                        if subrule == 'ε':
                            new_tokens = rest_tokens
                        else:
                            sub_tokens = _tokenise(subrule, terms, all_nts)
                            new_tokens = sub_tokens + rest_tokens
                            
                        new_seq = ''.join(new_tokens)
                        if new_seq not in seen:
                            seen.add(new_seq)
                            queue.append(new_tokens)
                    changed = True
        renamed_prods = new_productions

    # Final cleanup to ensure GNF form
    final_productions = {}
    for nt in renamed_prods:
        normalized = []
        for rhs in renamed_prods[nt]:
            if rhs == 'ε':
                if nt == new_start:
                    normalized.append(rhs)
                continue
                
            tokens = _tokenise(rhs, terms, all_nts)
            if not tokens:
                if nt == new_start:
                    normalized.append('ε')
                continue
                
            if tokens[0] in terms:
                normalized.append(rhs)
            else:
                # Replace leading nonterminal with its productions
                for subrule in renamed_prods[tokens[0]]:
                    if subrule == 'ε':
                        new_rhs = ''.join(tokens[1:]) or 'ε'
                    else:
                        new_rhs = subrule + ''.join(tokens[1:])
                    normalized.append(new_rhs)
        if normalized:
            final_productions[nt] = normalized

    gnf_nonterms = set(final_productions.keys())
    if new_start not in gnf_nonterms:
        gnf_nonterms.add(new_start)
        final_productions[new_start] = ['ε']

    return Grammar(
        non_terminals=gnf_nonterms,
        terminals=terms,
        productions=final_productions,
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