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

