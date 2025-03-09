class State:
    def __init__(self, label=None):
        self.label = label  # Character label, None for epsilon
        self.edge1 = None   # First transition
        self.edge2 = None   # Second transition

class NFA:
    def __init__(self, initial=None, accept=None):
        self.initial = initial
        self.accept = accept

def shunt(infix):
    """Convert infix regular expression to postfix notation."""
    specials = {
        '*': 60,
        '+': 55,
        '?': 50,
        '.': 40,
        '|': 20
    }
    postfix = ''
    stack = []

    for c in infix:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                postfix += stack.pop()
            if stack:
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

def followes(state):
    """Compute the epsilon closure of a single state."""
    states = set()
    stack = [state]

    while stack:
        s = stack.pop()
        if s not in states:
            states.add(s)
            if s.label is None:  # Epsilon transition
                if s.edge1 is not None:
                    stack.append(s.edge1)
                if s.edge2 is not None:
                    stack.append(s.edge2)
    return states

def compileRegex(postfix):
    """Construct an ε-NFA from a postfix regular expression."""
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

def get_nfa_states(nfa):
    """Collect all reachable states in the NFA using BFS."""
    from collections import deque
    visited = set()
    queue = deque([nfa.initial])
    states = []
    while queue:
        state = queue.popleft()
        if state in visited:
            continue
        visited.add(state)
        states.append(state)
        if state.edge1 is not None:
            queue.append(state.edge1)
        if state.edge2 is not None:
            queue.append(state.edge2)
    return states

def epsilon_closure(states):
    """Compute the epsilon closure of a set of states."""
    closure = set()
    for state in states:
        closure.update(followes(state))
    return closure

def move(states, symbol):
    """Compute states reachable by consuming a symbol from a set of states."""
    next_states = set()
    for state in states:
        if state.label == symbol:
            if state.edge1 is not None:
                next_states.add(state.edge1)
    return next_states

def print_dfa_table(nfa):
    """Convert ε-NFA to DFA and print its transition table."""
    # Get all NFA states and assign IDs
    nfa_states = get_nfa_states(nfa)
    state_to_id = {state: i for i, state in enumerate(nfa_states)}
    
    # Get input symbols (excluding epsilon)
    symbols = set()
    for state in nfa_states:
        if state.label is not None:
            symbols.add(state.label)
    symbols = sorted(list(symbols))
    
    # DFA construction using subset construction
    from collections import deque
    # Initial DFA state is the epsilon closure of NFA's initial state
    initial_closure = epsilon_closure({nfa.initial})
    initial_ids = frozenset(state_to_id[state] for state in initial_closure)
    dfa_states = [initial_ids]
    dfa_transitions = {}
    queue = deque([initial_ids])
    marked = set()
    
    while queue:
        current = queue.popleft()
        if current in marked:
            continue
        marked.add(current)
        for symbol in symbols:
            # Compute next states
            move_states = move([nfa_states[id] for id in current], symbol)
            next_closure = epsilon_closure(move_states)
            next_ids = frozenset(state_to_id[state] for state in next_closure) if next_closure else frozenset()
            if next_ids not in dfa_states:
                dfa_states.append(next_ids)
                queue.append(next_ids)
            # Record transition
            if current not in dfa_transitions:
                dfa_transitions[current] = {}
            dfa_transitions[current][symbol] = next_ids
    
    # Identify accepting DFA states
    dfa_accepting = set()
    for dfa_state in dfa_states:
        if any(nfa_states[id] == nfa.accept for id in dfa_state):
            dfa_accepting.add(dfa_state)
    
    # Assign readable names to DFA states (A, B, C, ...)
    dfa_state_names = {state: chr(65 + i) for i, state in enumerate(dfa_states)}
    
    # Print DFA transition table
    print("DFA Transition Table:")
    header = "State\t" + "\t".join(symbols)
    print(header)
    for dfa_state in dfa_states:
        state_name = dfa_state_names[dfa_state]
        is_initial = " (initial)" if dfa_state == initial_ids else ""
        is_accept = " (accept)" if dfa_state in dfa_accepting else ""
        row = f"{state_name}{is_initial}{is_accept}\t"
        for symbol in symbols:
            next_state = dfa_transitions.get(dfa_state, {}).get(symbol, None)
            if next_state:
                row += f"{dfa_state_names[next_state]}\t"
            else:
                row += "{}\t"  # Empty set indicates no transition
        print(row.rstrip())

def print_nfa_table(nfa):
    """Print the transition table for the ε-NFA."""
    from collections import deque
    visited = set()
    queue = deque([nfa.initial])
    states = []
    symbols = set()
    state_to_id = {}

    while queue:
        state = queue.popleft()
        if state in visited:
            continue
        visited.add(state)
        states.append(state)
        if state.label is not None:
            symbols.add(state.label)
        if state.edge1 is not None:
            queue.append(state.edge1)
        if state.edge2 is not None:
            queue.append(state.edge2)

    for i, state in enumerate(states):
        state_to_id[state] = i

    symbols = sorted(symbols)
    print("State\t" + "\t".join(symbols) + "\tε")

    for state in states:
        state_id = state_to_id[state]
        is_initial = " (initial)" if state == nfa.initial else ""
        is_accept = " (accept)" if state == nfa.accept else ""
        print(f"{state_id}{is_initial}{is_accept}", end="\t")

        for symbol in symbols:
            if state.label == symbol:
                next_states = []
                if state.edge1 is not None:
                    next_states.append(state_to_id[state.edge1])
                if state.edge2 is not None:
                    next_states.append(state_to_id[state.edge2])
                print("{" + ",".join(map(str, next_states)) + "}", end="\t")
            else:
                print("{}", end="\t")

        if state.label is None:
            next_states = []
            if state.edge1 is not None:
                next_states.append(state_to_id[state.edge1])
            if state.edge2 is not None:
                next_states.append(state_to_id[state.edge2])
            print("{" + ",".join(map(str, next_states)) + "}", end="\t")
        else:
            print("{}", end="\t")
        print()

def match_nfa(nfa, s):
    """Match a string against the ε-NFA."""
    current = set(followes(nfa.initial))
    nextStates = set()

    for c in s:
        for state in current:
            if state.label == c:
                follow = followes(state.edge1)
                nextStates.update(follow)
        current = nextStates
        nextStates = set()

    return nfa.accept in current

def main():
    """Main function to test the NFA and DFA construction."""
    infixes = ["a.b.c*", "a.(b|d).c*", "(a.(b|d))*", "a.(b.b)*.c"]
    strings = ["", "abc", "abbc", "abcc", "abad", "abbbc"]

    for infix in infixes:
        postfix = shunt(infix)
        nfa = compileRegex(postfix)
        
        print(f"NFA for infix: {infix}")
        print_nfa_table(nfa)
        print("\nDFA Transition Table:")
        print_dfa_table(nfa)
        print()
        
        for s in strings:
            result = match_nfa(nfa, s)
            print(("True " if result else "False ") + infix + " " + s)
        print()

if __name__ == "__main__":
    main()