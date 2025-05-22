from flat.grammar.grammar import Grammar
from flat.grammar.cyk import is_word_in_grammar

def run_grammar_test(title, non_terminals, terminals, productions, start_symbol, test_words=None):
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")

    grammar = Grammar(
        non_terminals=non_terminals,
        terminals=terminals,
        productions=productions,
        start_symbol=start_symbol
    )

    print("\nOriginal Grammar:")
    print(grammar)

    # print("\nType identification:")
    # print("Grammar type:", grammar.identify_type())
    # print("Is regular:", grammar.is_regular())
    # print("Is context-free:", grammar.is_context_free())
    # print("Is context-sensitive:", grammar.is_context_sensitive())
    #
    # print("\nEpsilon productions present:", grammar.has_epsilon_productions())
    # print("Unit productions present:", grammar.has_unit_productions())

    # try:
    #     grammar_no_epsilon = grammar.eliminate_epsilon_productions()
    #     print("\nGrammar after eliminating ε-productions:")
    #     print(grammar_no_epsilon)
    # except NotImplementedError:
    #     print("eliminate_epsilon_productions: NotImplementedError raised as expected.")
    #
    # try:
    #     grammar_no_units = grammar.eliminate_unit_productions()
    #     print("\nGrammar after eliminating unit productions:")
    #     print(grammar_no_units)
    # except NotImplementedError:
    #     print("eliminate_unit_productions: NotImplementedError raised as expected.")

    # try:
    #     grammar_no_units = grammar.simplify()
    #     print("\nGrammar after all simplifications:")
    #     print(grammar_no_units)
    # except NotImplementedError:
    #     print("simplify: NotImplementedError raised as expected.")

    try:
        cnf_grammar = grammar.to_cnf()
        print("\nCNF Grammar:")
        print(cnf_grammar)
        
        # Test words with CYK if provided
        if test_words:
            print("\nCYK Tests:")
            for word in test_words:
                print(f"\nTesting word: {word}")
                result = is_word_in_grammar(grammar, word, show_table=True)
                print(f"Result: {'Accepted' if result else 'Rejected'}")
    except NotImplementedError:
        print("cnf: Not good man, not good.")

    try:
        gnf_grammar = grammar.to_gnf()
        print("\nGNF Grammar:")
        print(gnf_grammar)
    except NotImplementedError:
        print("gnf: Not good man, not good.")

def main():
    # Grammar 1: Contains ε and unit productions
    run_grammar_test(
        "Grammar 1: Regular-style with ε and unit productions",
        non_terminals={"S", "A"},
        terminals={"a", "b"},
        productions={
            "S": ["ε", "A", "bA"],
            "A": ["aA", "a"]
        },
        start_symbol="S",
        test_words=["", "a", "aa", "aaa", "b", "ba", "baa"]
    )

    # Grammar 2: More complex CFG with ε and unit productions
    run_grammar_test(
        "Grammar 2: Context-Free with ε and unit productions",
        non_terminals={"S", "B", "C"},
        terminals={"a", "b", "c"},
        productions={
            "S": ["BC", "B", "C", "ε"],
            "B": ["b", "ε"],
            "C": ["c", "B"]
        },
        start_symbol="S",
        test_words=["", "b", "c", "bc", "bb", "cc"]
    )

    # Grammar 3: Unit chains and epsilon
    run_grammar_test(
        "Grammar 3: Chain of unit productions and ε",
        non_terminals={"S", "A", "B", "C"},
        terminals={"x"},
        productions={
            "S": ["A"],
            "A": ["B"],
            "B": ["C"],
            "C": ["x", "ε"]
        },
        start_symbol="S",
        test_words=["", "x"]
    )

    # Grammar 4: CFG with multiple nullable symbols
    run_grammar_test(
        "Grammar 4: Multiple nullable non-terminals",
        non_terminals={"S", "A", "B"},
        terminals={"a", "b"},
        productions={
            "S": ["AB", "a"],
            "A": ["a", "ε"],
            "B": ["b", "ε"]
        },
        start_symbol="S",
        test_words=["", "a", "b", "ab"]
    )

    # Grammar 5: Right-linear grammar with ε and unit productions
    run_grammar_test(
        "Grammar 5: Right-linear with ε and unit",
        non_terminals={"S", "A"},
        terminals={"a", "b"},
        productions={
            "S": ["aA", "bS", "ε"],
            "A": ["S"]
        },
        start_symbol="S",
        test_words=["", "a", "b", "ab", "ba", "aba"]
    )

    # Grammar 6: Left-recursive CFG with nullable non-terminal
    run_grammar_test(
        "Grammar 6: Left-recursive and nullable",
        non_terminals={"S", "A"},
        terminals={"x"},
        productions={
            "S": ["AS", "x"],
            "A": ["ε"]
        },
        start_symbol="S",
        test_words=["x", "xx", "xxx"]
    )

    # Grammar 7: Mixed unit and nullable across several paths
    run_grammar_test(
        "Grammar 7: Mixed unit and nullable",
        non_terminals={"S", "A", "B", "C"},
        terminals={"a", "b"},
        productions={
            "S": ["A"],
            "A": ["B", "ε"],
            "B": ["C"],
            "C": ["a", "b"]
        },
        start_symbol="S",
        test_words=["", "a", "b"]
    )

    # Grammar 8: Unit production pointing to epsilon rule
    run_grammar_test(
        "Grammar 8: Unit to epsilon",
        non_terminals={"S", "A"},
        terminals={"a"},
        productions={
            "S": ["A"],
            "A": ["ε"]
        },
        start_symbol="S",
        test_words=["", "a"]
    )

    # Grammar 9: Simple CFG no terminals, only unit + epsilon
    run_grammar_test(
        "Grammar 9: Only unit and epsilon",
        non_terminals={"S", "A", "B", "C"},
        terminals={"ε", "a", "b", "c"},
        productions={
            "S": ["B", "Ca"],
            "A": ["ε"],
            "B": ["ε", "A", "aA", "aaAbb", "bbb"],
            "C": ["abc"],
        },
        start_symbol="S",
        test_words=["", "abc", "aaa", "bbb", "aaabb"]
    )

    # Grammar 10: CFG with nested nullable chains
    run_grammar_test(
        "Grammar 10: Nested nullable chains",
        non_terminals={"S", "A", "B"},
        terminals={"a"},
        productions={
            "S": ["A"],
            "A": ["B"],
            "B": ["ε", "a"]
        },
        start_symbol="S",
        test_words=["", "a"]
    )

    # G = ({S, X, A, B}, {a, b}, {S → XA | BB, B → b | SB, X → b, A → a})
    run_grammar_test(
        "Grammar 11: GNF test",
        non_terminals={"S", "A", "B", "C"},
        terminals={"a", "b"},
        productions={
            "S": ["CA", "BB"],
            "A": ["a"],
            "B": ["b", "SB"],
            "C": ["b"],
        },
        start_symbol="S",
        test_words=["ba", "bb", "bbb", "bbba"]
    )


if __name__ == "__main__":
    main()
