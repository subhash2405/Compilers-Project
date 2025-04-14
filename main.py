import RegextoNFA 
import DFAtoMINDFA
import nfatodfa


def main():
    infix = "a.b|c*"
    test_string = "ab"
    # infixes = ["a.b.c*", "a.(b|d).c*", "(a.(b|d))*", "a.(b.b)*.c"]
    # strings = ["", "abc", "abbc", "abcc", "abad", "abbbc"]
    print(f"Processing regular expression: {infix}\n")
    
    # Step 1: Convert to postfix and build ε-NFA
    postfix = RegextoNFA.shunt(infix)
    nfa = RegextoNFA.compileRegex(postfix)
    
    # Step 2: Print ε-NFA transition table and get necessary data
    trans, state_to_id, alphabet = RegextoNFA.print_nfa_table(nfa)
    
    # Step 3: Convert to DFA and print its transition table
    dfa_states, dfa_transitions, dfa_initial, dfa_accepting = nfatodfa.build_dfa(nfa, trans, state_to_id, alphabet)
    nfatodfa.print_dfa_table(dfa_states, dfa_transitions, dfa_initial, dfa_accepting, alphabet)
    
    # Step 4: Minimize DFA and print the minimal DFA transition table
    min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting = DFAtoMINDFA.minimize_dfa(
        dfa_states, dfa_transitions, dfa_accepting, alphabet
    )
    DFAtoMINDFA.print_min_dfa_table(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet)

    print(DFAtoMINDFA.validate_string(test_string,min_dfa_transitions,min_dfa_initial,min_dfa_accepting, alphabet))

if __name__ == "__main__":
    main()