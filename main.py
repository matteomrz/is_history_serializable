import sys
from collections import defaultdict

def parse_history(args: list[str]) -> list[tuple[bool, int, str]]:
    # Each operation is encoded as three consecutive args: <r|w> <transaction_id> <variable>
    history = []
    for i in range(0, len(args), 3):
        try:
            # For creating the conflict graph it is sufficient
            # to know whether an operation is a write operation
            is_w: bool = args[i].lower() == "w"
            t_idx: int = int(args[i + 1])
            var: str = args[i + 2]
            history.append((is_w, t_idx, var))
        except TypeError | IndexError as e:
            raise ValueError(f"Malformed transaction input: {e}")

    return history


def get_conflict_graph(history: list[tuple[bool, int, str]]) -> dict[int, set]:
    # Build the conflict graph of the transaction history.
    # Nodes: Transactions from the history (T1, T2, ...)
    # Edges: Edge from Ti to Tj if there exists two operations in conflict pi and pj and pi <H pj
    graph: dict[int, set] = defaultdict(set)

    for i, (is_w_i, t_idx_i, var_i) in enumerate(history):
        for j in range(i + 1, len(history)):
            is_w_j, t_idx_j, var_j = history[j]

            # Operations are in conflict if they are from two different transactions,
            # target the same variable and at least one of them is a write operation
            is_t_different = t_idx_j != t_idx_i
            is_same_var = var_i == var_j
            is_w = is_w_i or is_w_j

            if is_t_different and is_same_var and is_w:
                # Add directed edge from the transaction of the first listed operation to the
                # transaction of the second operations
                graph[t_idx_i].add(t_idx_j)

    return graph


def has_cycle(graph: dict[int,set]) -> bool:
    # Detect cycles in the directed graph via Depth-first Search (DFS)

    # visited:
    #   Nodes which paths have been fully explored already.
    #   No cycle can be reached from these nodes.
    visited = []

    # current:
    #   Nodes included in the current DFS path, reaching an ancestor
    #   is equivalent to a cycle in the graph
    current = []

    def is_in_cycle(node):
        # Skip nodes already fully explored in a previous DFS call
        if node in visited:
            return False

        current.append(node)
        for neighbor in graph[node]:
            # Found back edge to ancestor -> Cycle
            if neighbor in current:
                return True

            # Check if the neighbor is part of a cycle
            elif is_in_cycle(neighbor):
                return True

        # No path found from the node that leads to itself or an ancestor
        # -> No cycle involving this node
        current.remove(node)
        visited.append(node)
        return False

    t_idxes = list(graph.keys())
    return any(is_in_cycle(node) for node in t_idxes)


def is_serializable(args: list[str]) -> bool:
    # A history is conflict-serializable <-> its conflict graph is acyclic
    history = parse_history(args)
    graph = get_conflict_graph(history)
    return not has_cycle(graph)


def main():
    args = sys.argv[1:]
    print(str(is_serializable(args)).lower())

# Example Usage:
# python main.py w 1 x r 2 x w 2 y r 3 y w 3 z r 1 z
if __name__ == "__main__":
    main()
