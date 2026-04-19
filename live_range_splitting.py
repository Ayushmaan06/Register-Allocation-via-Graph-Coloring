"""Cooper & Simpson (1998) demo: split-vs-spill decision with containment.

This script models two live ranges where l1 contains l2 (loop-like situation),
then compares spilling l1 entirely vs. splitting l1 around l2.
"""


def buildContainmentGraph():
    # Edge (lj -> li): li is live at a def/use point of lj.
    edges = [("l2", "l1")]

    graph = {
        "l1": {
            "blocked_colors_in_loop": {0},  # l2 occupies R0 in the hot loop region
            "spill_entire": {"loads": 11, "stores": 10},
            "split_by_color": {
                0: {"loads": 4, "stores": 3},
                1: {"loads": 1, "stores": 1},
            },
        },
        "l2": {"assigned_color": 0},
    }
    return graph, edges


def computeSplitCost(l, color, graph):
    ops = graph[l]["split_by_color"][color]
    return ops["loads"] + ops["stores"]


def findColor(l, graph, k):
    best = None
    blocked = graph[l]["blocked_colors_in_loop"]

    for color in range(k):
        if color in blocked:
            continue
        split_cost = computeSplitCost(l, color, graph)
        if best is None or split_cost < best[1]:
            best = (color, split_cost)

    return best


def compareSpillVsSplit():
    graph, edges = buildContainmentGraph()

    print("=== CONTAINMENT GRAPH ===")
    for src, dst in edges:
        print(f"{src} -> {dst}")

    spill_ops = graph["l1"]["spill_entire"]
    spill_cost = spill_ops["loads"] + spill_ops["stores"]

    print("\n=== COST COMPARISON ===")
    print(
        f"Spill l1 entirely: LOADs={spill_ops['loads']}, "
        f"STOREs={spill_ops['stores']}, total={spill_cost}"
    )

    choice = findColor("l1", graph, k=2)
    if choice is None:
        print("No legal color for splitting. Decision: SPILL")
        return

    color, split_cost = choice
    split_ops = graph["l1"]["split_by_color"][color]
    print(
        f"Split l1 across l2 with R{color}: "
        f"LOADs={split_ops['loads']}, STOREs={split_ops['stores']}, total={split_cost}"
    )

    print("\n=== DECISION ===")
    if split_cost < spill_cost:
        print(
            f"SPLIT: total {split_cost} < spill total {spill_cost}. "
            "Splitting avoids repeated loop traffic."
        )

        print("\n=== RESULTING CODE STRUCTURE ===")
        print("before loop:   R1 <- l1")
        print("before loop:   STORE [l1_slot], R1   # handoff to memory at loop boundary")
        print("[loop]:        l2 stays in R0; l1 is not kept in a register")
        print("after loop:    LOAD R1, [l1_slot]    # restore l1 after hot region")
        print("after loop:    continue with l1 in R1")
    else:
        print(f"SPILL: total {spill_cost} <= split total {split_cost}.")


if __name__ == "__main__":
    compareSpillVsSplit()
