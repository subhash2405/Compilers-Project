def generate_assembly(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet, test_string):
    state_to_int = {state: idx for idx, state in enumerate(min_dfa_states)}
    num_states = len(min_dfa_states)  # 5 states: A, B, C, D, E
    dead_state = num_states  # Dead state is 5

    initial_state = state_to_int[min_dfa_initial]  # 'A' -> 0
    accepting_states = {state_to_int[state] for state in min_dfa_accepting}  # {'A', 'C', 'D'} -> {0, 2, 3}
    transitions = {}
    for state in min_dfa_states:
        transitions[state_to_int[state]] = {char: state_to_int[next_state] 
                                           for char, next_state in min_dfa_transitions[state].items()}

    trans = [[dead_state] * 256 for _ in range(num_states + 1)]
    for state in range(num_states):
        for char in alphabet:
            trans[state][ord(char)] = transitions[state][char]

    accepting = [1 if state in accepting_states else 0 for state in range(num_states + 1)]

    trans_table_str = "trans_table:\n"
    for state in range(num_states + 1):
        trans_table_str += "    db " + ", ".join(map(str, trans[state])) + "\n"

    accepting_states_str = "accepting_states:\n    db " + ", ".join(map(str, accepting)) + "\n"

    input_str_str = "input_str: db " + ", ".join(f"'{c}'" for c in test_string) + ", 0\n"

    # Assembly code (x86 Linux)
    asm_code = f"""section .data
{trans_table_str}
{accepting_states_str}
{input_str_str}
accepted_str: db "Accepted", 10, 0
rejected_str: db "Rejected", 10, 0

section .text
global _start

_start:
    mov esi, input_str          ; Pointer to input string
    mov ebx, {initial_state}    ; Initial state (A = 0)

loop:
    mov al, [esi]               ; Load current character
    cmp al, 0                   ; Check for null terminator
    je check_accept

    movzx eax, al               ; Zero-extend char to eax
    mov ecx, ebx                ; Current state to ecx
    shl ecx, 8                  ; ecx = state * 256 (shift left by 8 bits)
    add ecx, eax                ; ecx = state * 256 + char
    mov bl, [trans_table + ecx] ; Next state to bl
    movzx ebx, bl               ; Zero-extend bl to ebx
    inc esi                     ; Move to next character
    jmp loop

check_accept:
    cmp byte [accepting_states + ebx], 1
    je accept
    jmp reject

accept:
    mov eax, 4                  ; sys_write
    mov ebx, 1                  ; stdout
    mov ecx, accepted_str
    mov edx, 10                 ; Length of "Accepted\\n"
    int 0x80
    jmp end

reject:
    mov eax, 4                  ; sys_write
    mov ebx, 1                  ; stdout
    mov ecx, rejected_str
    mov edx, 10                 ; Length of "Rejected\\n"
    int 0x80
    jmp end

end:
    mov eax, 1                  ; sys_exit
    mov ebx, 0                  ; Return code 0
    int 0x80
"""
    return asm_code

# Example usage with your DFA data
min_dfa_states = ['A', 'B', 'C', 'D', 'E']
min_dfa_transitions = {
    'A': {'a': 'B', 'b': 'E', 'c': 'C'},
    'B': {'a': 'E', 'b': 'D', 'c': 'E'},
    'C': {'a': 'E', 'b': 'E', 'c': 'C'},
    'D': {'a': 'E', 'b': 'E', 'c': 'E'},
    'E': {'a': 'E', 'b': 'E', 'c': 'E'}
}
min_dfa_initial = 'A'
min_dfa_accepting = {'A', 'C', 'D'}
alphabet = {'a', 'b', 'c'}
test_string = "ab"

asm_code = generate_assembly(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet, test_string)
with open("regex.asm", "w") as f:
    f.write(asm_code)
print("Assembly code generated in 'regex.asm'")