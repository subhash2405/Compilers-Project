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

def matchRegex(infix, s):
    postfix = shunt(infix)
    nfa = compileRegex(postfix)
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

def match_nfa(nfa, s):
    """Match a string against an already compiled NFA."""
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

def print_nfa_table(nfa):
    """Print the NFA state table in the terminal."""
    from collections import deque
    # Traverse the NFA to collect all states and symbols
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

    # Assign unique IDs to each state
    for i, state in enumerate(states):
        state_to_id[state] = i

    # Sort symbols for consistent column ordering
    symbols = sorted(symbols)

    # Print table header
    print("State\t" + "\t".join(symbols) + "\tε")

    # Print table rows
    for state in states:
        state_id = state_to_id[state]
        is_initial = " (initial)" if state == nfa.initial else ""
        is_accept = " (accept)" if state == nfa.accept else ""
        print(f"{state_id}{is_initial}{is_accept}", end="\t")

        # Transitions for each input symbol
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

        # Epsilon transitions
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

def main():
    infixes = ["a.b.c*", "a.(b|d).c*", "(a.(b|d))*", "a.(b.b)*.c"]
    strings = ["", "abc", "abbc", "abcc", "abad", "abbbc"]

    for infix in infixes:
        # Compile the NFA once per infix
        postfix = shunt(infix)
        nfa = compileRegex(postfix)
        
        # Print the NFA state table
        print(f"NFA for infix: {infix}")
        print_nfa_table(nfa)
        
        # Match each string using the compiled NFA
        for s in strings:
            result = match_nfa(nfa, s)
            print(("True " if result else "False ") + infix + " " + s)
        print()

if __name__ == "__main__":
    main()