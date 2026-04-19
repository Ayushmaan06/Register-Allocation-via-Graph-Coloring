"""Park & Moon (2004) demo: optimistic coalescing with undo.

This script shows how aggressive coalescing can be attempted first, then undone
when the merged node is uncolorable. It compares spills against a conservative
baseline for k=2 registers.
"""

from copy import deepcopy


def buildGraph():
    adj = {
        "p": {"q", "x", "y"},
        "q": {"p", "x", "y"},
        "x": {"p", "q"},
        "y": {"p", "q"},
    }
    return {
        "adj": adj,
        "copy_pairs": [("x", "y")],
        "spill_costs": {"p": 20, "q": 20, "x": 1, "y": 1},
        "merged": {},
    }


def printGraph(title, adj):
    print(title)
    for n in sorted(adj):
        print(f"  {n}: {sorted(adj[n])}")


def pickSpillCandidate(work, spill_costs):
    return min(work, key=lambda n: (spill_costs.get(n, 10) / max(1, len(work[n])), n))


def simplifyAndSelect(graph, k):
    work = deepcopy(graph["adj"])
    stack = []

    print("=== SIMPLIFY PHASE ===")
    while work:
        low = sorted([n for n in work if len(work[n]) < k], key=lambda n: (len(work[n]), n))
        if low:
            node = low[0]
            stack.append((node, False))
            print(f"simplify node {node} (degree={len(work[node])})")
        else:
            node = pickSpillCandidate(work, graph.get("spill_costs", {}))
            stack.append((node, True))
            ratio = graph.get("spill_costs", {}).get(node, 10) / max(1, len(work[node]))
            print(f"spill-candidate {node} (cost/degree={ratio:.2f})")

        for nb in list(work[node]):
            work[nb].discard(node)
        del work[node]

    colors = {}
    spills = set()
    print("=== SELECT PHASE ===")
    while stack:
        node, was_candidate = stack.pop()
        used = {colors[nb] for nb in graph["adj"][node] if nb in colors}
        avail = [c for c in range(k) if c not in used]
        if avail:
            colors[node] = avail[0]
            tag = " (was spill-candidate)" if was_candidate else ""
            print(f"color {node} -> R{avail[0]}{tag}")
        else:
            spills.add(node)
            print(f"color {node} -> SPILL")

    return colors, spills


def aggressiveCoalesce(graph):
    g = deepcopy(graph)
    for x, y in g["copy_pairs"]:
        if x not in g["adj"] or y not in g["adj"] or y in g["adj"][x]:
            continue

        merged = f"{x}+{y}"
        x_nb = set(g["adj"][x])
        y_nb = set(g["adj"][y])
        new_nb = (x_nb | y_nb) - {x, y}

        for nb in new_nb:
            g["adj"][nb].discard(x)
            g["adj"][nb].discard(y)
            g["adj"][nb].add(merged)

        del g["adj"][x]
        del g["adj"][y]
        g["adj"][merged] = new_nb

        g["merged"][merged] = {"parts": (x, y), "x_nb": x_nb, "y_nb": y_nb}
        g["spill_costs"].pop(x, None)
        g["spill_costs"].pop(y, None)
        g["spill_costs"][merged] = 1
        print(f"Coalesced copy-related pair ({x}, {y}) -> {merged}")

    return g


def undoCoalesce(node, graph):
    info = graph["merged"][node]
    x, y = info["parts"]

    for nb in list(graph["adj"][node]):
        graph["adj"][nb].discard(node)
    del graph["adj"][node]

    graph["adj"][x] = set(info["x_nb"])
    graph["adj"][y] = set(info["y_nb"])
    graph["adj"][x].discard(y)
    graph["adj"][y].discard(x)

    for nb in graph["adj"][x]:
        if nb in graph["adj"]:
            graph["adj"][nb].add(x)
    for nb in graph["adj"][y]:
        if nb in graph["adj"]:
            graph["adj"][nb].add(y)

    graph["spill_costs"][x] = 1
    graph["spill_costs"][y] = 1
    graph["spill_costs"].pop(node, None)
    return x, y


def tryColorSplits(x, y, graph):
    # Split x,y into hot/cold pieces to salvage partial coloring after undo.
    base = deepcopy(graph)
    for n in [x, y]:
        for nb in list(base["adj"][n]):
            base["adj"][nb].discard(n)
        del base["adj"][n]

    p, q = "p", "q"
    split_nodes = {
        f"{x}_pre": {p},
        f"{x}_hot": {p, q},
        f"{y}_pre": {q},
        f"{y}_hot": {q},
    }
    for sn, nbs in split_nodes.items():
        base["adj"][sn] = set(nbs)
        for nb in nbs:
            base["adj"][nb].add(sn)

    base["spill_costs"] = {n: 20 for n in base["adj"]}
    base["spill_costs"][f"{x}_hot"] = 1

    colors, spills = simplifyAndSelect(base, 2)
    return base, colors, spills


def main():
    k = 2
    original = buildGraph()

    printGraph("=== GRAPH BEFORE COALESCING ===", original["adj"])
    print("\n=== CONSERVATIVE COALESCING BASELINE ===")
    _, base_spills = simplifyAndSelect(original, k)

    print("\n=== AGGRESSIVE COALESCING ===")
    optimistic = aggressiveCoalesce(original)
    printGraph("Graph after coalescing", optimistic["adj"])

    print("\n=== ALLOCATE COALESCED GRAPH ===")
    _, merged_spills = simplifyAndSelect(optimistic, k)

    final_colors = {}
    final_spills = set(merged_spills)
    for n in list(merged_spills):
        if n in optimistic["merged"]:
            print(f"\nMerged node {n} is uncolorable -> undoCoalesce()")
            x, y = undoCoalesce(n, optimistic)
            _, final_colors, final_spills = tryColorSplits(x, y, optimistic)
            break

    print("\n=== FINAL COLORING AFTER UNDO ===")
    for n in sorted(final_colors):
        print(f"{n} -> R{final_colors[n]}")
    for n in sorted(final_spills):
        print(f"{n} -> SPILL")

    print("\n=== SPILL COMPARISON ===")
    print(f"Conservative coalescing spills: {len(base_spills)}")
    print(f"Optimistic coalescing spills:   {len(final_spills)}")


if __name__ == "__main__":
    main()
