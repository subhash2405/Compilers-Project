from collections import deque

def epsilon_closure(state_ids, trans):
    """Compute the epsilon closure of a set of state IDs."""
    closure = set(state_ids)
    stack = list(state_ids)
    while stack:
        state_id = stack.pop()
        for next_id in trans[state_id]['ε']:
            if next_id not in closure:
                closure.add(next_id)
                stack.append(next_id)
    return frozenset(closure)

# Compute the set of states reachable by a symbol
def move(state_ids, symbol, trans):
    """Compute the set of states reachable by a symbol from a set of state IDs."""
    next_states = set()
    for state_id in state_ids:
        next_states.update(trans[state_id][symbol])
    return frozenset(next_states)

# Build the DFA from the ε-NFA
def build_dfa(nfa, trans, state_to_id, alphabet):
    """Build a DFA from the ε-NFA using subset construction."""
    initial_closure = epsilon_closure({state_to_id[nfa.initial]}, trans)
    dfa_states = [initial_closure]
    dfa_transitions = {}
    queue = deque([initial_closure])
    marked = set()
    
    while queue:
        current = queue.popleft()
        if current in marked:
            continue
        marked.add(current)
        for symbol in alphabet:
            next_move = move(current, symbol, trans)
            if next_move:
                next_closure = epsilon_closure(next_move, trans)
                if next_closure not in dfa_states:
                    dfa_states.append(next_closure)
                    queue.append(next_closure)
                dfa_transitions[(current, symbol)] = next_closure
            else:
                dfa_transitions[(current, symbol)] = frozenset()
    
    # Add dead state (empty set) if not present and set its transitions
    if frozenset() not in dfa_states:
        dfa_states.append(frozenset())
    for symbol in alphabet:
        dfa_transitions[(frozenset(), symbol)] = frozenset()
    
    # Identify accepting states
    dfa_accepting = {state for state in dfa_states if state_to_id[nfa.accept] in state}
    return dfa_states, dfa_transitions, initial_closure, dfa_accepting

# Print the DFA transition table
def print_dfa_table(dfa_states, dfa_transitions, dfa_initial, dfa_accepting, alphabet):
    """Print the transition table for the DFA."""
    dfa_state_names = {state: chr(65 + i) for i, state in enumerate(dfa_states)}
    print("\nDFA Transition Table:")
    header = "State\t" + "\t".join(alphabet)
    print(header)
    for dfa_state in dfa_states:
        state_name = dfa_state_names[dfa_state]
        is_initial = " (initial)" if dfa_state == dfa_initial else ""
        is_accept = " (accept)" if dfa_state in dfa_accepting else ""
        row = f"{state_name}{is_initial}{is_accept}\t"
        for symbol in alphabet:
            next_state = dfa_transitions.get((dfa_state, symbol), frozenset())
            row += dfa_state_names.get(next_state, "{}") + "\t"
        print(row.rstrip())

