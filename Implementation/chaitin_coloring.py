"""Chaitin (1982) demo: graph-coloring register allocation with simplification and spilling.

This script simulates simplify/select allocation on two small interference graphs with k=3:
1) a graph that forces a spill
2) a graph that is fully colorable
"""

from copy import deepcopy


def buildInterferenceGraph(case_name="spill"):
    if case_name == "spill":
        # K4 core (A,B,C,D) forces at least one spill with k=3.
        adj = {
            "A": {"B", "C", "D", "E"},
            "B": {"A", "C", "D", "E"},
            "C": {"A", "B", "D", "F"},
            "D": {"A", "B", "C", "F"},
            "E": {"A", "B"},
            "F": {"C", "D"},
        }
        spill_costs = {"A": 12, "B": 10, "C": 8, "D": 3, "E": 6, "F": 7}
    else:
        # 3-colorable graph with moderate pressure.
        adj = {
            "A": {"B", "C"},
            "B": {"A", "C", "D"},
            "C": {"A", "B", "E"},
            "D": {"B", "F"},
            "E": {"C", "G"},
            "F": {"D", "G"},
            "G": {"E", "F"},
        }
        spill_costs = {"A": 8, "B": 7, "C": 9, "D": 5, "E": 5, "F": 4, "G": 6}
    return adj, spill_costs


def spillHeuristic(graph, spill_costs):
    best_node = None
    best_ratio = float("inf")
    for node, neighbors in graph.items():
        degree = max(1, len(neighbors))
        ratio = spill_costs[node] / degree
        if ratio < best_ratio:
            best_ratio = ratio
            best_node = node
    return best_node


def simplify(graph, k, spill_costs):
    work = deepcopy(graph)
    stack = []
    step = 1

    print("=== SIMPLIFY PHASE ===")
    while work:
        low_degree = sorted([n for n in work if len(work[n]) < k], key=lambda n: (len(work[n]), n))
        if low_degree:
            node = low_degree[0]
            stack.append((node, False))
            print(f"Step {step}: simplify node {node} (degree={len(work[node])})")
        else:
            node = spillHeuristic(work, spill_costs)
            degree = len(work[node])
            ratio = spill_costs[node] / max(1, degree)
            stack.append((node, True))
            print(
                f"Step {step}: spill-chosen node {node} "
                f"(cost={spill_costs[node]}, degree={degree}, cost/degree={ratio:.2f})"
            )

        for nb in list(work[node]):
            work[nb].remove(node)
        del work[node]
        step += 1

    return stack


def select(stack, graph, k):
    colors = {}
    spills = set()

    print("=== SELECT PHASE ===")
    while stack:
        node, was_spill_choice = stack.pop()
        used = {colors[nb] for nb in graph[node] if nb in colors}
        available = [r for r in range(k) if r not in used]

        if available:
            colors[node] = available[0]
            tag = " (was spill-candidate)" if was_spill_choice else ""
            print(f"Select {node}: assign R{available[0]}{tag}")
        else:
            spills.add(node)
            print(f"Select {node}: no color available -> SPILL")

    return colors, spills


def run_case(case_name, k=3):
    graph, costs = buildInterferenceGraph(case_name)
    stack = simplify(graph, k, costs)
    colors, spills = select(stack, graph, k)

    print("=== RESULT ===")
    total_spill = 0
    for n in sorted(graph):
        if n in spills:
            print(f"{n} -> SPILL")
            total_spill += costs[n]
        else:
            print(f"{n} -> R{colors[n]}")
    print(f"Total spill cost: {total_spill}")
    print()


def main():
    print("##### CASE 1: Spill is required (k=3) #####")
    run_case("spill", k=3)

    print("##### CASE 2: Fully colorable (k=3) #####")
    run_case("colorable", k=3)


if __name__ == "__main__":
    main()
