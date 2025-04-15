import RegextoNFA 
import DFAtoMINDFA
import nfatodfa
from test_generation import generate_assembly
import os
import sys

def write_min_dfa_dot(states, transitions, start_state, accepting_states, filename):
    dot_lines = []
    dot_lines.append("digraph DFA {")
    dot_lines.append("    rankdir=LR;")
    dot_lines.append("    node [shape = point ]; qi;")

    # Map states to simple names like S0, S1, ...
    state_names = {}
    for i, state in enumerate(states):
        state_names[state] = f"S{i}"

    # Accepting states
    dot_lines.append("    node [shape = doublecircle];")
    for state in accepting_states:
        dot_lines.append(f"    {state_names[state]};")

    dot_lines.append("    node [shape = circle];")
    dot_lines.append(f"    qi -> {state_names[start_state]};")

    for from_state, trans in transitions.items():
        for symbol, to_state in trans.items():
            dot_lines.append(f'    {state_names[from_state]} -> {state_names[to_state]} [ label = "{symbol}" ];')

    dot_lines.append("}")

    with open(filename, "w") as f:
        f.write("\n".join(dot_lines))


def main():
    # Check if test index was passed as an argument
    test_index = sys.argv[1] if len(sys.argv) > 1 else 1  # Default to 1 if not provided
    infix = input("Enter infix expression:")
    print()
    test_string = input("Enter test expression:")
    print()
    print(f"Processing regular expression: {infix}\n")
    
    postfix = RegextoNFA.shunt(infix)
    nfa = RegextoNFA.compileRegex(postfix)
    
    trans, state_to_id, alphabet = RegextoNFA.print_nfa_table(nfa)
    
    dfa_states, dfa_transitions, dfa_initial, dfa_accepting = nfatodfa.build_dfa(nfa, trans, state_to_id, alphabet)
    nfatodfa.print_dfa_table(dfa_states, dfa_transitions, dfa_initial, dfa_accepting, alphabet)
    
    min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting = DFAtoMINDFA.minimize_dfa(
        dfa_states, dfa_transitions, dfa_accepting, alphabet
    )
    DFAtoMINDFA.print_min_dfa_table(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet)

    print("\nValidation result:")
    print(DFAtoMINDFA.validate_string(test_string, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet))

    # Generate and write assembly code
    asm_code = generate_assembly(
        min_dfa_states,
        min_dfa_transitions,
        min_dfa_initial,
        min_dfa_accepting,
        alphabet,
        test_string
    )

    with open("regex.asm", "w") as f:
        f.write(asm_code)
    print("\nAssembly code generated in 'regex.asm'")

    dot_output_dir = "/Users/siddharthsingh/Documents/Compilers-Project/minimal_dfa_graphs"
    os.makedirs(dot_output_dir, exist_ok=True)

    # Use the test_index to generate a unique file name for each test case
    base_filename = f"graph{test_index}"
    dot_file_path = os.path.join(dot_output_dir, f"{base_filename}.dot")

    write_min_dfa_dot(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, dot_file_path)
    print(f"Graphviz .dot file saved to: {dot_file_path}")


if __name__ == "__main__":
    main()
