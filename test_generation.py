# generate_asm.py

def generate_assembly(min_dfa_states, min_dfa_transitions, min_dfa_initial, min_dfa_accepting, alphabet, test_string):
    state_to_int = {state: idx for idx, state in enumerate(min_dfa_states)}
    num_states = len(min_dfa_states)
    dead_state = num_states

    initial_state = state_to_int[min_dfa_initial]
    accepting_states = {state_to_int[state] for state in min_dfa_accepting}
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

    asm_code = f"""section .data
{trans_table_str}
{accepting_states_str}
{input_str_str}
accepted_str: db "Accepted", 10, 0
rejected_str: db "Rejected", 10, 0

section .text
global _start

_start:
    mov esi, input_str
    mov ebx, {initial_state}

loop:
    mov al, [esi]
    cmp al, 0
    je check_accept

    movzx eax, al
    mov ecx, ebx
    shl ecx, 8
    add ecx, eax
    mov bl, [trans_table + ecx]
    movzx ebx, bl
    inc esi
    jmp loop

check_accept:
    cmp byte [accepting_states + ebx], 1
    je accept
    jmp reject

accept:
    mov eax, 4
    mov ebx, 1
    mov ecx, accepted_str
    mov edx, 10
    int 0x80
    jmp end

reject:
    mov eax, 4
    mov ebx, 1
    mov ecx, rejected_str
    mov edx, 10
    int 0x80
    jmp end

end:
    mov eax, 1
    mov ebx, 0
    int 0x80
"""
    return asm_code
