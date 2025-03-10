from collections import deque

def find(parent, i):
    """Find the root of element i with path compression."""
    if parent[i] != i:
        parent[i] = find(parent, parent[i])
    return parent[i]

def union(parent, i, j):
    """Merge sets containing i and j."""
    pi = find(parent, i)
    pj = find(parent, j)
    if pi != pj:
        parent[pi] = pj

# Minimize the DFA
def minimize_dfa(dfa_states, dfa_transitions, dfa_accepting, alphabet):
    """Minimize the DFA using the table-filling method."""
    if not dfa_states:
        return [], {}, None, set()
    state_indices = {state: i for i, state in enumerate(dfa_states)}
    
    # Initialize distinguishable pairs
    distinguishable = set()
    for i in range(len(dfa_states)):
        for j in range(i + 1, len(dfa_states)):
            state_i = dfa_states[i]
            state_j = dfa_states[j]
            if (state_i in dfa_accepting) != (state_j in dfa_accepting):
                distinguishable.add((i, j))
    
    # Mark distinguishable pairs iteratively
    changed = True
    while changed:
        changed = False
        for i in range(len(dfa_states)):
            for j in range(i + 1, len(dfa_states)):
                if (i, j) not in distinguishable:
                    for symbol in alphabet:
                        next_i = dfa_transitions.get((dfa_states[i], symbol), frozenset())
                        next_j = dfa_transitions.get((dfa_states[j], symbol), frozenset())
                        ni_idx = state_indices.get(next_i, -1)
                        nj_idx = state_indices.get(next_j, -1)
                        pair = (min(ni_idx, nj_idx), max(ni_idx, nj_idx))
                        if pair in distinguishable and pair != (-1, -1):
                            distinguishable.add((i, j))
                            changed = True
                            break
    
    # Group equivalent states using union-find
    parent = list(range(len(dfa_states)))
    for i in range(len(dfa_states)):
        for j in range(i + 1, len(dfa_states)):
            if (i, j) not in distinguishable:
                union(parent, i, j)
    
    # Build equivalence classes
    equiv_classes = {}
    for i in range(len(dfa_states)):
        root = find(parent, i)
        if root not in equiv_classes:
            equiv_classes[root] = set()
        equiv_classes[root].add(i)
    
    # Define minimal DFA states
    min_dfa_states = [frozenset(class_set) for class_set in equiv_classes.values()]
    
    # Determine initial and accepting states
    min_dfa_initial = None
    min_dfa_accepting = set()
    for class_set in min_dfa_states:
        if 0 in class_set:  # dfa_states[0] is initial
            min_dfa_initial = frozenset(class_set)
        for idx in class_set:
            if dfa_states[idx] in dfa_accepting:
                min_dfa_accepting.add(frozenset(class_set))
                break
    
    # Build minimal DFA transitions
    min_dfa_transitions = {}
    for class_set in min_dfa_states:
        rep_idx = min(class_set)
        rep_state = dfa_states[rep_idx]
        min_state = frozenset(class_set)
        min_dfa_transitions[min_state] = {}
        for symbol in alphabet:
            next_state = dfa_transitions.get((rep_state, symbol), frozenset())
            next_idx = state_indices.get(next_state, -1)
            if next_idx != -1:
                next_root = find(parent, next_idx)
                min_dfa_transitions[min_state][symbol] = frozenset(equiv_classes[next_root])
            else:
                min_dfa_transitions[min_state][symbol] = frozenset()
    
    return min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting

# Print the minimal DFA transition table
def print_min_dfa_table(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet):
    """Print the transition table for the minimal DFA."""
    min_dfa_state_names = {state: chr(65 + i) for i, state in enumerate(min_dfa_states)}
    print("\nMinimal DFA Transition Table:")
    header = "State\t" + "\t".join(alphabet)
    print(header)
    for min_state in min_dfa_states:
        state_name = min_dfa_state_names[min_state]
        is_initial = " (initial)" if min_state == min_dfa_initial else ""
        is_accept = " (accept)" if min_state in min_dfa_accepting else ""
        row = f"{state_name}{is_initial}{is_accept}\t"
        for symbol in alphabet:
            next_state = min_dfa_transitions[min_state].get(symbol, frozenset())
            row += min_dfa_state_names.get(next_state, "{}") + "\t"
        print(row.rstrip())
