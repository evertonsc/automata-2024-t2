from typing import List, Tuple, Dict, Set

def load_automata(filename: str) -> Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]]:
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
    with open(filename, "rt", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines()]

    if len(lines) < 5:
        raise ValueError("Arquivo inválido: número insuficiente de linhas.")

    alphabet = lines[0].split()
    states = lines[1].split()
    final_states = lines[2].split()
    initial_state = lines[3]

    transitions = []
    for line in lines[4:]:
        origin, symbol, destination = line.split()
        transitions.append((origin, symbol, destination))

    if not set(final_states).issubset(states):
        raise ValueError("Estado final inválido.")
    if initial_state not in states:
        raise ValueError("Estado inicial inválido.")

    for origin, symbol, destination in transitions:
        if origin not in states or destination not in states:
            raise ValueError(f"Estado na transição inválido: {origin} ou {destination}")
        if symbol != '&' and symbol not in alphabet:
            raise ValueError(f"Símbolo na transição inválido: {symbol}")

    return states, alphabet, transitions, initial_state, final_states

def process(automaton: Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]], words: List[str]) -> \
        Dict[str, str]:
    """
    Processa a lista de palavras e retora o resultado.

    Os resultados válidos são ACEITA, REJEITA, INVALIDA.
    """
    states, alphabet, delta, initial_state, final_states = automaton
    results = {}

    for word in words:
        if any(char not in alphabet for char in word):
            results[word] = "INVALIDA"
            continue

        current_state = initial_state
        valid = True
        for symbol in word:
            next_state = None
            for origin, sym, dest in delta:
                if origin == current_state and sym == symbol:
                    next_state = dest
                    break
            if next_state:
                current_state = next_state
            else:
                valid = False
                break

        if valid and current_state in final_states:
            results[word] = "ACEITA"
        else:
            results[word] = "REJEITA"

    return results

def handle_closure(state: str, delta: List[Tuple[str, str, str]]) -> Set[str]:
    """
    Retorna o fecho de um estado em um NFA.
    """
    closure = {state}
    stack = [state]

    while stack:
        current = stack.pop()
        closure.update(dest for origin, sym, dest in delta if origin == current and sym == '&' and dest not in closure)
        stack.extend(dest for origin, sym, dest in delta if origin == current and sym == '&' and dest not in closure)

    return closure

def convert_to_dfa(automaton: Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]]) -> Tuple[
    List[str], List[str], List[Tuple[str, str, str]], str, List[str]]:
    """Converte um NFA num DFA."""
    states, alphabet, delta, initial_state, final_states = automaton

    def find_transitions(states_set: Set[str], symbol: str) -> Set[str]:
        return {dest for state in states_set for origin, sym, dest in delta if origin == state and sym == symbol}

    def epsilon_closure(states_set: Set[str]) -> Set[str]:
        closure = set(states_set)
        stack = list(states_set)

        while stack:
            current_state = stack.pop()
            for origin, sym, dest in delta:
                if origin == current_state and sym == '&' and dest not in closure:
                    closure.add(dest)
                    stack.append(dest)

        return closure

    def state_to_str(state_set: Set[str]) -> str:
        return ','.join(sorted(state_set))

    initial_closure = epsilon_closure({initial_state})
    queue = [initial_closure]
    visited = []
    new_states = []
    new_delta = []
    new_final_states = []

    while queue:
        current_closure = queue.pop(0)
        current_str = state_to_str(current_closure)
        if current_closure not in visited:
            visited.append(current_closure)
            new_states.append(current_str)

            if current_closure & set(final_states):
                new_final_states.append(current_str)

            for symbol in alphabet:
                next_closure = epsilon_closure(find_transitions(current_closure, symbol))
                if next_closure:
                    next_str = state_to_str(next_closure)
                    new_delta.append((current_str, symbol, next_str))
                    if next_closure not in visited:
                        queue.append(next_closure)

    new_initial_state = state_to_str(initial_closure)
    return new_states, alphabet, new_delta, new_initial_state, new_final_states
