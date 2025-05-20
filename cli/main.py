"""Command-line interface for FLAT-Tool.

This module provides a command-line interface for interacting with the FLAT-Tool.
It allows users to perform various operations on grammars and automata.
"""

import argparse
import sys
import json
from pathlib import Path

from flat.grammar import (
    Grammar, GrammarType, identify_grammar_type,
    simplify_grammar, convert_to_cnf, convert_to_gnf
)
from flat.automata import NFA, DFA, nfa_to_dfa
from flat.regex import RegularExpression, dfa_to_regex, regex_to_nfa
from flat.io import parse_bnf, parse_json, parse_text, format_bnf, format_json, format_text


def main():
    """Main entry point for the FLAT-Tool CLI."""
    parser = argparse.ArgumentParser(description="FLAT-Tool: Formal Languages and Automata Theory Toolkit")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Grammar type identification command
    type_parser = subparsers.add_parser("type", help="Identify grammar type")
    type_parser.add_argument("input_file", help="Input file containing grammar definition")
    type_parser.add_argument("--format", choices=["bnf", "json", "text"], default="bnf",
                           help="Input format (default: bnf)")
    
    # Grammar simplification command
    simplify_parser = subparsers.add_parser("simplify", help="Simplify grammar")
    simplify_parser.add_argument("input_file", help="Input file containing grammar definition")
    simplify_parser.add_argument("--format", choices=["bnf", "json", "text"], default="bnf",
                               help="Input format (default: bnf)")
    simplify_parser.add_argument("--output-format", choices=["bnf", "json", "text"], default="bnf",
                                help="Output format (default: bnf)")
    simplify_parser.add_argument("--output-file", help="Output file (default: stdout)")
    
    # CNF conversion command
    cnf_parser = subparsers.add_parser("cnf", help="Convert grammar to Chomsky Normal Form")
    cnf_parser.add_argument("input_file", help="Input file containing grammar definition")
    cnf_parser.add_argument("--format", choices=["bnf", "json", "text"], default="bnf",
                          help="Input format (default: bnf)")
    cnf_parser.add_argument("--output-format", choices=["bnf", "json", "text"], default="bnf",
                           help="Output format (default: bnf)")
    cnf_parser.add_argument("--output-file", help="Output file (default: stdout)")
    
    # GNF conversion command
    gnf_parser = subparsers.add_parser("gnf", help="Convert grammar to Greibach Normal Form")
    gnf_parser.add_argument("input_file", help="Input file containing grammar definition")
    gnf_parser.add_argument("--format", choices=["bnf", "json", "text"], default="bnf",
                          help="Input format (default: bnf)")
    gnf_parser.add_argument("--output-format", choices=["bnf", "json", "text"], default="bnf",
                           help="Output format (default: bnf)")
    gnf_parser.add_argument("--output-file", help="Output file (default: stdout)")
    
    # NFA to DFA conversion command
    nfa_to_dfa_parser = subparsers.add_parser("nfa2dfa", help="Convert NFA to DFA")
    nfa_to_dfa_parser.add_argument("input_file", help="Input file containing NFA definition (JSON)")
    nfa_to_dfa_parser.add_argument("--output-file", help="Output file (default: stdout)")
    
    # Regex to NFA conversion command
    regex_to_nfa_parser = subparsers.add_parser("regex2nfa", help="Convert regular expression to NFA")
    regex_to_nfa_parser.add_argument("regex", help="Regular expression pattern")
    regex_to_nfa_parser.add_argument("--output-file", help="Output file (default: stdout)")
    
    # DFA to Regex conversion command
    dfa_to_regex_parser = subparsers.add_parser("dfa2regex", help="Convert DFA to regular expression")
    dfa_to_regex_parser.add_argument("input_file", help="Input file containing DFA definition (JSON)")
    dfa_to_regex_parser.add_argument("--output-file", help="Output file (default: stdout)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is provided, show help
    if not args.command:
        parser.print_help()
        return
    
    # Execute grammar-related commands
    if args.command in ["type", "simplify", "cnf", "gnf"]:
        # Load grammar from input file
        try:
            grammar = load_grammar(args.input_file, args.format)
        except Exception as e:
            print(f"Error loading grammar: {str(e)}", file=sys.stderr)
            return 1
        
        # Execute command
        if args.command == "type":
            grammar_type = identify_grammar_type(grammar)
            print(f"Grammar type: {grammar_type.name}")
            print(f"Type {grammar_type.value} in the Chomsky hierarchy")
            
        elif args.command == "simplify":
            simplified_grammar = simplify_grammar(grammar)
            output_grammar(simplified_grammar, args.output_format, args.output_file)
            
        elif args.command == "cnf":
            cnf_grammar = convert_to_cnf(grammar)
            output_grammar(cnf_grammar, args.output_format, args.output_file)
            
        elif args.command == "gnf":
            gnf_grammar = convert_to_gnf(grammar)
            output_grammar(gnf_grammar, args.output_format, args.output_file)
    
    # Execute automata-related commands
    elif args.command == "nfa2dfa":
        try:
            # Load NFA from JSON file
            nfa = load_automaton(args.input_file, NFA)
            # Convert NFA to DFA
            dfa = nfa_to_dfa(nfa)
            # Output DFA
            output_automaton(dfa, args.output_file)
        except Exception as e:
            print(f"Error converting NFA to DFA: {str(e)}", file=sys.stderr)
            return 1
    
    # Execute regex-related commands
    elif args.command == "regex2nfa":
        try:
            # Create RegularExpression from pattern
            regex = RegularExpression(args.regex)
            # Convert regex to NFA
            nfa = regex_to_nfa(regex)
            # Output NFA
            output_automaton(nfa, args.output_file)
        except Exception as e:
            print(f"Error converting regex to NFA: {str(e)}", file=sys.stderr)
            return 1
            
    elif args.command == "dfa2regex":
        try:
            # Load DFA from JSON file
            dfa = load_automaton(args.input_file, DFA)
            # Convert DFA to regex
            regex = dfa_to_regex(dfa)
            # Output regex
            output_regex(regex, args.output_file)
        except Exception as e:
            print(f"Error converting DFA to regex: {str(e)}", file=sys.stderr)
            return 1
    
    return 0


def load_grammar(input_file: str, format_type: str) -> Grammar:
    """Load a grammar from a file.
    
    Args:
        input_file: Path to the input file.
        format_type: Format of the input file (bnf, json, or text).
        
    Returns:
        Grammar: The loaded grammar.
        
    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the input file format is invalid.
    """
    # Check if file exists
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Read file content
    with open(input_path, "r") as f:
        content = f.read()
    
    # Parse grammar based on format
    if format_type == "bnf":
        return parse_bnf(content)
    elif format_type == "json":
        return parse_json(content)
    elif format_type == "text":
        return parse_text(content)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def output_grammar(grammar: Grammar, format_type: str, output_file: str = None):
    """Output a grammar to a file or stdout.
    
    Args:
        grammar: The grammar to output.
        format_type: Format of the output (bnf, json, or text).
        output_file: Path to the output file, or None for stdout.
    """
    # Format grammar based on format type
    if format_type == "bnf":
        output = format_bnf(grammar)
    elif format_type == "json":
        output = format_json(grammar)
    elif format_type == "text":
        output = format_text(grammar)
    else:
        raise ValueError(f"Unsupported format: {format_type}")
    
    # Write to file or stdout
    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
    else:
        print(output)


def load_automaton(input_file: str, automaton_class):
    """Load an automaton from a JSON file.
    
    Args:
        input_file: Path to the input file.
        automaton_class: The automaton class to instantiate (NFA or DFA).
        
    Returns:
        An automaton instance.
        
    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the input file format is invalid.
    """
    # Check if file exists
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Read file content
    with open(input_path, "r") as f:
        content = f.read()
    
    # Parse JSON
    try:
        data = json.loads(content)
        
        # Validate required fields
        required_fields = ['states', 'alphabet', 'transitions', 'initial_state', 'final_states']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert lists to sets where appropriate
        states = set(data['states'])
        alphabet = set(data['alphabet'])
        initial_state = data['initial_state']
        final_states = set(data['final_states'])
        transitions = data['transitions']
        
        # For NFA, convert transition values to sets
        if automaton_class == NFA:
            for state in transitions:
                for symbol in transitions[state]:
                    transitions[state][symbol] = set(transitions[state][symbol])
            
            # Check for epsilon in alphabet
            epsilon = 'ε'
            if epsilon in alphabet:
                alphabet.remove(epsilon)
            
            return NFA(
                states=states,
                alphabet=alphabet,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states,
                epsilon=epsilon
            )
        else:  # DFA
            return DFA(
                states=states,
                alphabet=alphabet,
                transitions=transitions,
                initial_state=initial_state,
                final_states=final_states
            )
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading automaton: {str(e)}")


def output_automaton(automaton, output_file: str = None):
    """Output an automaton to a file or stdout in JSON format.
    
    Args:
        automaton: The automaton to output (NFA or DFA).
        output_file: Path to the output file, or None for stdout.
    """
    # Convert automaton to dictionary
    data = {
        'states': list(automaton.states),
        'alphabet': list(automaton.alphabet),
        'initial_state': automaton.initial_state,
        'final_states': list(automaton.final_states),
        'transitions': {}
    }
    
    # Handle transitions based on automaton type
    if isinstance(automaton, NFA):
        # Include epsilon in alphabet if used
        if any(automaton.epsilon in symbols for state, symbols in automaton.transitions.items() 
               for symbol, _ in symbols.items()):
            data['alphabet'].append(automaton.epsilon)
        
        # Convert sets to lists in transitions
        for state, symbols in automaton.transitions.items():
            data['transitions'][state] = {}
            for symbol, targets in symbols.items():
                data['transitions'][state][symbol] = list(targets)
    else:  # DFA
        data['transitions'] = automaton.transitions
    
    # Convert to JSON
    output = json.dumps(data, indent=2)
    
    # Write to file or stdout
    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
    else:
        print(output)


def output_regex(regex, output_file: str = None):
    """Output a regular expression to a file or stdout.
    
    Args:
        regex: The RegularExpression to output.
        output_file: Path to the output file, or None for stdout.
    """
    # Get the pattern string
    output = regex.pattern
    
    # Write to file or stdout
    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())