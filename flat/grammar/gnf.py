#!/usr/bin/env python3
"""
Greibach Normal Form conversion module with guaranteed termination.
"""

from .grammar import Grammar
import itertools
from collections import deque

def _tokenise(text, terminals, non_terminals):
    """
    Split the string `text` into a list of symbols, choosing the
    longest-fitting nonterminal at each position first, then terminals.
    """
    out = []
    i = 0
    # sort nonterminals by descending length so that 'X10' is tried
    # before 'X1'
    sorted_nts = sorted(non_terminals, key=len, reverse=True)
    while i < len(text):
        matched = False
        for nt in sorted_nts:
            if text.startswith(nt, i):
                out.append(nt)
                i += len(nt)
                matched = True
                break
        if matched:
            continue
        # no nonterminal matched: try a single-character terminal
        ch = text[i]
        if ch in terminals:
            out.append(ch)
        else:
            # unknown symbol — either malformed grammar or treat
            # it as a terminal anyway
            out.append(ch)
        i += 1
    return out


def convert_to_gnf(grammar):
    """
    Convert the given grammar (assumed in CNF form, possibly with
    S -> ε if S is the start) into an equivalent Greibach Normal Form.
    """
    _aux_counter = itertools.count(1)
    def _new_nt():
        return f"A{next(_aux_counter)}"

    def eliminate_left_recursion(A, rules):
        """
        Given a nonterminal A and a set of its productions `rules`
        (each a string of symbols), eliminate direct left recursion.
        Returns a dict {X: set_of_rhs_strings}, introducing one new
        nonterminal if needed.
        """
        recursive = []
        nonrec = []
        for r in rules:
            if r.startswith(A):
                recursive.append(r[len(A):])
            else:
                nonrec.append(r)
        if not recursive:
            return {A: set(rules)}
        B = _new_nt()
        # if there are no nonrecursive, we still need one
        if not nonrec:
            return {
                A: {B},
                B: set(alpha + B for alpha in recursive) | {"ε"}
            }
        return {
            A: set(beta + B for beta in nonrec),
            B: set(alpha + B for alpha in recursive) | {"ε"}
        }

    # 1) start from the CNF grammar as given
    nonterms = sorted(grammar.non_terminals)
    prods = { A: set(grammar.productions.get(A, [])) for A in nonterms }
    start = grammar.start_symbol
    terms = set(grammar.terminals)

    # 2) rename all old nonterminals to A1, A2, … in a fixed order
    name_map = { start: _new_nt() }
    for A in nonterms:
        if A not in name_map:
            name_map[A] = _new_nt()

    renamed = {}
    for A in nonterms:
        A2 = name_map[A]
        renamed[A2] = set()
        for rhs in prods[A]:
            # simple character-by-character rewrite
            tokens = []
            i = 0
            while i < len(rhs):
                # try to match a mapped nonterminal
                matched = False
                for old in sorted(nonterms, key=len, reverse=True):
                    if rhs.startswith(old, i):
                        tokens.append(name_map[old])
                        i += len(old)
                        matched = True
                        break
                if matched:
                    continue
                # else single char
                tokens.append(rhs[i])
                i += 1
            renamed[A2].add("".join(tokens))

    all_nts = set(renamed)
    ordered = sorted(all_nts, key=lambda x: int(x[1:]))

    # 3) forward substitution & remove direct left recursion
    for i, A in enumerate(ordered):
        # for each B < A
        for j in range(i):
            B = ordered[j]
            newset = set()
            for rhs in renamed[A]:
                if rhs.startswith(B):
                    tail = rhs[len(B):]
                    for br in renamed[B]:
                        if br == "ε":
                            newset.add(tail or "ε")
                        else:
                            newset.add(br + tail)
                else:
                    newset.add(rhs)
            renamed[A] = newset
        # now eliminate A-A recursion
        elim = eliminate_left_recursion(A, renamed[A])
        # merge back into renamed, introduce new nonterm if any
        for X, s in elim.items():
            if X not in renamed:
                ordered.append(X)
            renamed[X] = s
        ordered = sorted(set(ordered), key=lambda x: int(x[1:]))

    # 4) now ensure every production starts with a terminal
    changed = True
    limit = 1000
    it = 0
    while changed and it < limit:
        it += 1
        changed = False
        newp = { A: set() for A in renamed }
        for A, rhss in renamed.items():
            for rhs in rhss:
                if rhs == "ε":
                    newp[A].add("ε")
                    continue
                toks = _tokenise(rhs, terms, all_nts)
                if toks and toks[0] in terms:
                    newp[A].add("".join(toks))
                else:
                    # BFS-expand leading nonterminal
                    queue = deque([toks])
                    seen = set()
                    while queue:
                        cur = queue.popleft()
                        if not cur:
                            newp[A].add("ε")
                            continue
                        if cur[0] in terms:
                            newp[A].add("".join(cur))
                            continue
                        N0, tail = cur[0], cur[1:]
                        if N0 not in renamed:
                            # treat it as terminal if unknown
                            terms.add(N0)
                            newp[A].add("".join(cur))
                            continue
                        for sub in renamed[N0]:
                            if sub == "ε":
                                nxt = tail
                            else:
                                nxt = _tokenise(sub, terms, all_nts) + tail
                            tup = tuple(nxt)
                            if tup not in seen:
                                seen.add(tup)
                                queue.append(nxt)
                                changed = True
        renamed = newp

    # 5) final cleanup: only start may have ε, drop ε elsewhere
    final = {}
    for A, rhss in renamed.items():
        clean = set()
        for rhs in rhss:
            if rhs == "ε":
                if A == name_map[start]:
                    clean.add(rhs)
            else:
                clean.add(rhs)
        if clean:
            final[A] = clean

    # 6) build the GNF grammar
    GNF_NT = set(final)
    GNF_start = name_map[start]
    # make sure start exists
    if GNF_start not in GNF_NT:
        GNF_NT.add(GNF_start)
        final[GNF_start] = {"ε"}

    return Grammar(
        non_terminals=GNF_NT,
        terminals=terms,
        productions=final,
        start_symbol=GNF_start
    )


def is_in_gnf(grammar):
    """
    Quick check: every production is either
      A -> ε   (only allowed if A is start)
    or A -> a α  with a in terminals, α a (maybe empty) string of nonterminals.
    """
    for A, rhss in grammar.productions.items():
        for rhs in rhss:
            if rhs == "ε":
                if A != grammar.start_symbol:
                    return False
            else:
                toks = []
                # naïve split: each NT is "A\d+" or each char if not NT
                i = 0
                while i < len(rhs):
                    # try longest NT
                    matched = False
                    for nt in sorted(grammar.non_terminals, key=len, reverse=True):
                        if rhs.startswith(nt, i):
                            toks.append(nt)
                            i += len(nt)
                            matched = True
                            break
                    if matched:
                        continue
                    toks.append(rhs[i])
                    i += 1
                if not toks or toks[0] not in grammar.terminals:
                    return False
                for sym in toks[1:]:
                    if sym not in grammar.non_terminals:
                        return False
    return True