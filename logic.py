"""
logic.py — ядро алгоритма «Игра в слова».
"""


class Node:
    """Узел односвязного списка."""

    def __init__(self, word: str):
        self.word: str = word
        self.next: "Node | None" = None


class LinkedList:
    """Односвязный список с хвостовым указателем."""

    def __init__(self):
        self.head: Node | None = None
        self.tail: Node | None = None
        self._size: int = 0

    def append(self, word: str) -> None:
        new_node = Node(word)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            if self.tail is not None:
                self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def to_list(self) -> list[str]:
        result: list[str] = []
        current = self.head
        while current is not None:
            result.append(current.word)
            current = current.next
        return result

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0


def effective_last_letter(word: str) -> str:
    """Возвращает последнюю букву слова, игнорируя «ь»."""
    i = len(word) - 1
    while i >= 0 and word[i] == "ь":
        i -= 1
    return word[i] if i >= 0 else word[-1]


def _in_out_degrees(words: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    out: dict[str, int] = {}
    inp: dict[str, int] = {}
    for word in words:
        u = word[0]
        v = effective_last_letter(word)
        out[u] = out.get(u, 0) + 1
        inp[v] = inp.get(v, 0) + 1
    return inp, out


def _all_vertices(words: list[str]) -> set[str]:
    vertices: set[str] = set()
    for word in words:
        vertices.add(word[0])
        vertices.add(effective_last_letter(word))
    return vertices


def _is_connected_for_euler(words: list[str]) -> bool:
    if not words:
        return True

    adj: dict[str, set[str]] = {}
    all_vertices = set()
    for word in words:
        u = word[0]
        v = effective_last_letter(word)
        all_vertices.add(u)
        all_vertices.add(v)
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)

    if not all_vertices:
        return True

    start = next(iter(all_vertices))
    visited: set[str] = set()
    queue = [start]
    while queue:
        node = queue.pop()
        if node in visited:
            continue
        visited.add(node)
        for nb in adj.get(node, set()):
            if nb not in visited:
                queue.append(nb)

    return all(v in visited for v in all_vertices)


def euler_cycle_exists(words: list[str]) -> bool:
    """
    Проверка существования Эйлерова цикла:
    1) in-degree == out-degree для всех вершин
    2) граф связен в неориентированном смысле
    """
    inp, out = _in_out_degrees(words)
    vertices = _all_vertices(words)

    for v in vertices:
        if inp.get(v, 0) != out.get(v, 0):
            return False

    return _is_connected_for_euler(words)


def find_chain(words: list[str]) -> LinkedList | None:
    """
    Алгоритм Иерхольцера (итеративный) для поиска Эйлерова цикла.
    Вершины — буквы, рёбра — слова. Возвращает цепочку или None.

    Перебираются все возможные стартовые вершины, чтобы гарантировать,
    что программа найдёт решение независимо от порядка слов в списке.
    """
    if not words:
        return None

    if not euler_cycle_exists(words):
        return None

    # Строим список смежности один раз
    base_adj: dict[str, list[int]] = {}
    for idx, word in enumerate(words):
        base_adj.setdefault(word[0], []).append(idx)

    for u in base_adj:
        base_adj[u].sort(reverse=True)

    # Перебираем все возможные стартовые вершины
    for start_letter in sorted(set(word[0] for word in words)):
        # Копируем adj для каждой попытки
        adj = {u: v.copy() for u, v in base_adj.items()}

        walk_stack_v: list[str] = [start_letter]
        walk_stack_e: list[int | None] = [None]
        circuit_edges_idx: list[int] = []

        while walk_stack_v:
            v = walk_stack_v[-1]
            if adj.get(v):
                idx = adj[v].pop()
                next_v = effective_last_letter(words[idx])
                walk_stack_v.append(next_v)
                walk_stack_e.append(idx)
            else:
                walk_stack_v.pop()
                e = walk_stack_e.pop()
                if e is not None:
                    circuit_edges_idx.append(e)

        circuit_edges_idx.reverse()

        if len(circuit_edges_idx) == len(words):
            chain = LinkedList()
            for idx in circuit_edges_idx:
                chain.append(words[idx])
            return chain

    return None


def read_words_from_file(filepath: str) -> list[str]:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    words = content.split()
    if not words:
        raise ValueError("Файл не содержит слов.")
    return words


def write_chain_to_file(filepath: str, chain: LinkedList | None) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        if chain is None:
            f.write("Решения не существует\n")
        else:
            f.write(" ".join(chain.to_list()) + "\n")