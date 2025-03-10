from collections import deque

# Define the State class for the ε-NFA
class State:
    def __init__(self, label=None):
        self.label = label  # Character label, None for epsilon
        self.edge1 = None   # First transition
        self.edge2 = None   # Second transition

# Define the NFA class to hold initial and accept states
class NFA:
    def __init__(self, initial=None, accept=None):
        self.initial = initial
        self.accept = accept

# Convert infix regular expression to postfix notation
def shunt(infix):
    """Convert infix regular expression to postfix notation."""
    specials = {'*': 60, '+': 55, '?': 50, '.': 40, '|': 20}
    postfix = ''
    stack = []
    for c in infix:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix += stack.pop()
            stack.pop()  # Remove '('
        elif c in specials:
            while stack and stack[-1] in specials and specials[c] <= specials[stack[-1]]:
                postfix += stack.pop()
            stack.append(c)
        else:
            postfix += c
    while stack:
        postfix += stack.pop()
    return postfix

# Construct an ε-NFA from a postfix regular expression
def compileRegex(postfix):
    """Construct an ε-NFA from a postfix regular expression using Thompson's construction."""
    nfaStack = []
    for c in postfix:
        if c == '*':
            nfa1 = nfaStack.pop()
            initial = State()
            accept = State()
            initial.edge1 = nfa1.initial
            initial.edge2 = accept
            nfa1.accept.edge1 = nfa1.initial
            nfa1.accept.edge2 = accept
            nfaStack.append(NFA(initial, accept))
        elif c == '.':
            nfa2 = nfaStack.pop()
            nfa1 = nfaStack.pop()
            nfa1.accept.edge1 = nfa2.initial
            nfaStack.append(NFA(nfa1.initial, nfa2.accept))
        elif c == '|':
            nfa2 = nfaStack.pop()
            nfa1 = nfaStack.pop()
            initial = State()
            accept = State()
            initial.edge1 = nfa1.initial
            initial.edge2 = nfa2.initial
            nfa1.accept.edge1 = accept
            nfa2.accept.edge1 = accept
            nfaStack.append(NFA(initial, accept))
        elif c == '+':
            nfa1 = nfaStack.pop()
            initial = State()
            accept = State()
            initial.edge1 = nfa1.initial
            nfa1.accept.edge1 = nfa1.initial
            nfa1.accept.edge2 = accept
            nfaStack.append(NFA(initial, accept))
        elif c == '?':
            nfa1 = nfaStack.pop()
            initial = State()
            accept = State()
            initial.edge1 = nfa1.initial
            initial.edge2 = accept
            nfa1.accept.edge1 = accept
            nfaStack.append(NFA(initial, accept))
        else:  # Literal character
            initial = State(c)
            accept = State()
            initial.edge1 = accept
            nfaStack.append(NFA(initial, accept))
    return nfaStack.pop()

# Collect all reachable states in the ε-NFA and assign IDs
def get_nfa_state_ids(nfa):
    """Collect all reachable states in the NFA and assign integer IDs."""
    visited = set()
    queue = deque([nfa.initial])
    states = []
    while queue:
        state = queue.popleft()
        if state not in visited:
            visited.add(state)
            states.append(state)
            if state.edge1 is not None:
                queue.append(state.edge1)
            if state.edge2 is not None:
                queue.append(state.edge2)
    state_to_id = {state: i for i, state in enumerate(states)}
    return states, state_to_id

# Print the ε-NFA transition table
def print_nfa_table(nfa):
    """Print the transition table for the ε-NFA."""
    states, state_to_id = get_nfa_state_ids(nfa)
    alphabet = sorted(set(state.label for state in states if state.label is not None))
    trans = {state_id: {symbol: set() for symbol in alphabet + ['ε']} for state_id in range(len(states))}
    
    # Build transition dictionary
    for state in states:
        state_id = state_to_id[state]
        if state.label is not None:
            if state.edge1 is not None:
                trans[state_id][state.label].add(state_to_id[state.edge1])
        else:
            if state.edge1 is not None:
                trans[state_id]['ε'].add(state_to_id[state.edge1])
            if state.edge2 is not None:
                trans[state_id]['ε'].add(state_to_id[state.edge2])
    
    # Print the table
    print("ε-NFA Transition Table:")
    header = "State\t" + "\t".join(alphabet) + "\tε"
    print(header)
    for state_id in range(len(states)):
        is_initial = " (initial)" if states[state_id] == nfa.initial else ""
        is_accept = " (accept)" if states[state_id] == nfa.accept else ""
        row = f"{state_id}{is_initial}{is_accept}\t"
        for symbol in alphabet:
            next_states = trans[state_id][symbol]
            row += "{" + ",".join(map(str, sorted(next_states))) + "}\t"
        epsilon_next = trans[state_id]['ε']
        row += "{" + ",".join(map(str, sorted(epsilon_next))) + "}"
        print(row)
    return trans, state_to_id, alphabet

# Compute the epsilon closure of a set of state IDs
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

# Union-find functions for DFA minimization
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

# Main function to process the regex and print tables at each step
def main():
    # Example regular expression (replace with your input)
    infix = "a.b"
    infixes = ["a.b.c*", "a.(b|d).c*", "(a.(b|d))*", "a.(b.b)*.c"]
    strings = ["", "abc", "abbc", "abcc", "abad", "abbbc"]
    print(f"Processing regular expression: {infix}\n")
    
    # Step 1: Convert to postfix and build ε-NFA
    postfix = shunt(infix)
    nfa = compileRegex(postfix)
    
    # Step 2: Print ε-NFA transition table and get necessary data
    trans, state_to_id, alphabet = print_nfa_table(nfa)
    
    # Step 3: Convert to DFA and print its transition table
    dfa_states, dfa_transitions, dfa_initial, dfa_accepting = build_dfa(nfa, trans, state_to_id, alphabet)
    print_dfa_table(dfa_states, dfa_transitions, dfa_initial, dfa_accepting, alphabet)
    
    # Step 4: Minimize DFA and print the minimal DFA transition table
    min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting = minimize_dfa(
        dfa_states, dfa_transitions, dfa_accepting, alphabet
    )
    print_min_dfa_table(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet)

if __name__ == "__main__":
    main()