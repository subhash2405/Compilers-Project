import RegextoNFA 
import DFAtoMINDFA
import nfatodfa
from test_generation import generate_assembly

def main():
    infix = input("Enter infix expression:")
    test_string = input("Enter test expression:")
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
    print(DFAtoMINDFA.validate_string(test_string,min_dfa_transitions,min_dfa_initial,min_dfa_accepting, alphabet))

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

if __name__ == "__main__":
    main()
