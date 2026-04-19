"""Odaira et al. (2010) demo: coloring-based coalescing after splitting.

This script hardcodes split ranges (A1/A2/A3, B1/B2/B3, C1/C2), runs trial
coloring with extended colors, coalesces companion sub-ranges, and compares
spill counts against no-coalescing allocation.
"""

from collections import defaultdict
from copy import deepcopy


def buildSplitGraph():
    adj = {
        "A1": {"B1", "C1", "C2"},
        "A2": {"B1", "C1", "C2"},
        "A3": {"B1", "C1"},
        "B1": {"A1", "A2", "A3", "C1", "C2"},
        "B2": {"C1", "C2"},
        "B3": {"C1", "C2"},
        "C1": {"A1", "A2", "A3", "B1", "B2", "B3", "C2"},
        "C2": {"A1", "A2", "B1", "B2", "B3", "C1"},
    }
    copy_edges = [("A1", "A2"), ("A2", "A3"), ("B1", "B2"), ("B2", "B3"), ("C1", "C2")]
    return {"adj": adj, "copy_edges": copy_edges}


def trialColoring(graph, k):
    order = ["B1", "C1", "C2", "B2", "B3", "A1", "A2", "A3"]
    colors = {}

    print("=== TRIAL COLORING (real + extended colors) ===")
    for n in order:
        used = {colors[nb] for nb in graph["adj"][n] if nb in colors}
        c = 0
        while c in used:
            c += 1
        colors[n] = c
        tag = "real" if c < k else "extended"
        print(f"{n} -> color {c} ({tag})")

    return colors


def findCompanions(coloring, graph):
    parent = {n: n for n in graph["adj"]}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    not_coalesced = []

    for a, b in graph["copy_edges"]:
        if coloring[a] != coloring[b]:
            not_coalesced.append((a, b, "different colors"))
            continue
        if b in graph["adj"][a]:
            not_coalesced.append((a, b, "interfere directly"))
            continue
        union(a, b)

    groups = defaultdict(list)
    for n in graph["adj"]:
        groups[find(n)].append(n)

    companions = [sorted(v) for v in groups.values() if len(v) > 1]

    print("\n=== COMPANION SUB-RANGES ===")
    if companions:
        for g in companions:
            print(f"coalesce candidate: {g}")
    else:
        print("No companion groups found.")

    print("\n=== NOT COALESCED ===")
    for a, b, reason in not_coalesced:
        print(f"{a} and {b}: {reason}")

    return companions


def coalesceCompanions(graph, companions):
    rep = {}
    for group in companions:
        name = "+".join(group)
        for n in group:
            rep[n] = name

    for n in graph["adj"]:
        rep.setdefault(n, n)

    new_adj = defaultdict(set)
    for u, nbs in graph["adj"].items():
        ru = rep[u]
        for v in nbs:
            rv = rep[v]
            if ru != rv:
                new_adj[ru].add(rv)
                new_adj[rv].add(ru)

    return {"adj": {k: set(v) for k, v in new_adj.items()}, "copy_edges": []}


def finalColoring(graph, k):
    adj = graph["adj"]
    work = deepcopy(adj)
    stack = []

    while work:
        low = sorted([n for n in work if len(work[n]) < k], key=lambda n: (len(work[n]), n))
        if low:
            node = low[0]
            stack.append(node)
        else:
            node = sorted(work, key=lambda n: (len(work[n]), n))[0]
            stack.append(node)

        for nb in list(work[node]):
            work[nb].remove(node)
        del work[node]

    colors = {}
    spills = set()
    while stack:
        node = stack.pop()
        used = {colors[nb] for nb in adj[node] if nb in colors}
        avail = [c for c in range(k) if c not in used]
        if avail:
            colors[node] = avail[0]
        else:
            spills.add(node)

    return colors, spills


def print_result(title, colors, spills):
    print(title)
    for n in sorted(colors):
        print(f"{n} -> R{colors[n]}")
    for n in sorted(spills):
        print(f"{n} -> SPILL")


def main():
    k = 3
    graph = buildSplitGraph()

    base_colors, base_spills = finalColoring(graph, k)

    trial = trialColoring(graph, k)
    companions = findCompanions(trial, graph)
    coalesced = coalesceCompanions(graph, companions)

    final_colors, final_spills = finalColoring(coalesced, k)

    print("\n=== FINAL COLORING AFTER COALESCING ===")
    print_result("", final_colors, final_spills)

    print("\n=== SPILL COUNT COMPARISON ===")
    print(f"Baseline (no coalescing): {len(base_spills)}")
    print(f"Coloring-based coalescing: {len(final_spills)}")


if __name__ == "__main__":
    main()
