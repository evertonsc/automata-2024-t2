"""Implementação de autômatos finitos."""
def load_automata(filename: str):
    """
    Lê os dados de um autômato finito a partir de um arquivo.

    A estrutura do arquivo deve ser:

    <lista de símbolos do alfabeto, separados por espaço (' ')>
    <lista de nomes de estados>
    <lista de nomes de estados finais>
    <nome do estado inicial>
    <lista de regras de transição, com "origem símbolo destino">

    Um exemplo de arquivo válido é:

    ```
    a b
    q0 q1 q2 q3
    q0 q3
    q0
    q0 a q1
    q0 b q2
    q1 a q0
    q1 b q3
    q2 a q3
    q2 b q0
    q3 a q1
    q3 b q2
    ```

    Caso o arquivo seja inválido uma exceção Exception é gerada.

    """
    with open(filename, "rt", encoding="utf-8") as arquivo:
        lines = arquivo.readlines()

    alphabet = tuple(lines[0].strip().split())
    states = tuple(lines[1].strip().split())
    final_states = tuple(lines[2].strip().split())
    initial_state = lines[3].strip()
    delta = [tuple(line.strip().split()) for line in lines[4:]]

    if initial_state not in states:
        raise ValueError("Estado inicial inválido")

    if any(state not in states for state in final_states):
        raise ValueError("Estado final inválido")

    if any(
            edge[0] not in states or
            (edge[1] not in alphabet and edge[1] != '&') or
            edge[2] not in states
            for edge in delta
    ):
        raise ValueError("Edge inválido")

    return states, alphabet, delta, initial_state, final_states


def process(automata, words):
    """
    Processa a lista de palavras e retora o resultado.

    Os resultados válidos são ACEITA, REJEITA, INVALIDA.
    """
    states, alphabet, delta, initial_state, final_states = automata
    result = {}

    for word in words:
        current_state = initial_state
        is_valid_word = True

        for symbol in word:
            if symbol not in alphabet:
                result[word] = "INVALIDA"
                is_valid_word = False
                break

            for edge in delta:
                if edge[0] == current_state and edge[1] == symbol:
                    current_state = edge[2]
                    break

        if is_valid_word:
            result[word] = "ACEITA" if current_state in final_states else "REJEITA"

    return result


def handle_closure(state, delta):
    """Retorna o fecho de um estado em um NFA."""
    closure = {state}
    stack = [state]

    while stack:
        current = stack.pop()
        closure.update(
            edge[2] for edge in delta if edge[0] == current and edge[1] == '&'
        )
        stack.extend(
            edge[2] for edge in delta if edge[0] == current and edge[1] == '&' and edge[2] not in closure
        )

    return closure


def convert_to_dfa(automata):
    """Converte um NFA num DFA."""
    alphabet, delta, initial_state, final_states = automata[1:]
    initial_closure = handle_closure(initial_state, delta)
    new_states = [initial_closure]
    new_delta = []
    queue = [initial_closure]
    state_map = {"".join(sorted(initial_closure)): initial_closure}

    while queue:
        current_closure = queue.pop(0)
        current_closure_name = "".join(sorted(current_closure))

        for symbol in alphabet:
            next_closure = set()

            for state in current_closure:
                next_closure.update(
                    handle_closure(edge[2], delta)
                    for edge in delta if edge[0] == state and edge[1] == symbol
                )

            next_closure_name = "".join(sorted(next_closure))

            if next_closure_name not in state_map:
                state_map[next_closure_name] = next_closure
                new_states.append(next_closure)
                queue.append(next_closure)

            new_delta.append((current_closure_name, symbol, next_closure_name))

    new_final_states = [
        "".join(sorted(state))
        for state in new_states if any(substate in final_states for substate in state)
    ]

    new_initial_state = "".join(sorted(initial_closure))

    return tuple(state_map.keys()), alphabet, new_delta, new_initial_state, new_final_states
