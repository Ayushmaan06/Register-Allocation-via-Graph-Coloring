
<!-- Beautified summary.md: structured, with headings and bullet lists -->

# Innovations and Heuristics in Register Coalescing

## Executive Summary

Global register allocation models the problem as a graph-coloring task and must balance two competing goals:

- eliminate copy instructions (coalescing) to reduce dynamic instruction count and improve performance
- avoid spilling (moving values to memory), which is usually far more expensive than keeping a temporary for a short time

This summary condenses the main ideas from five foundational papers and highlights the practical trade-offs that guide modern allocators.

## Quick Takeaways

- Coalescing can be both helpful and harmful: merging two nodes reduces copies but may increase the merged node's degree, causing spills.
- Conservative heuristics avoid creating uncolorable graphs but miss many safe coalescing opportunities.
- Optimistic coalescing coalesces aggressively and undoes merges later if they cause spills — often reducing the overall spill cost.
- Coloring-based coalescing uses a trial coloring (with extra colors) to identify "companions" that are safe to coalesce after splitting.
- Empirical results in the literature show non-trivial spill reductions and runtime improvements when using optimistic or coloring-based strategies.

---

## Foundations: the Interference Graph

- **Nodes** — live ranges (variables/temporaries).
- **Edges** — two nodes interfere when their lifetimes overlap and thus cannot share a register.
- **Colors (K)** — the number of physical registers available.

### Chaitin-style allocation (overview)

1. Build the interference graph from liveness analysis.
2. (Optional) Coalesce copy-related non-interfering nodes.
3. Simplify: repeatedly remove nodes with degree < K and push them onto a stack.
4. Spill decision: when only degree ≥ K nodes remain, choose a spill candidate (commonly minimizing cost/degree).
5. Select: pop the stack and assign colors; any node that cannot be colored becomes an actual spill (insert loads/stores and retry).

---

## The Coalescing Trade-off

Coalescing affects neighbors' degrees in two opposite ways:

- **Negative impact**: The merged node inherits the union of neighbors → its degree increases and may break colorability.
- **Positive impact**: A shared neighbor that interferes with both operands loses one interfering edge after coalescing → its degree decreases and may become colorable.

Deciding when to coalesce is therefore a cost/benefit trade-off.

---

## Evolution of Coalescing Heuristics

### Aggressive Coalescing (early work)

- Coalesce any non-interfering copy pair.
- *Pro*: maximizes copy elimination.
- *Con*: can create high-degree nodes and force spills.

### Conservative Coalescing (Briggs et al.)

- Coalesce only when simple heuristics predict colorability is preserved.
- *Pro*: avoids turning a colorable graph uncolorable.
- *Con*: overly cautious — many safe coalesces are missed.

### Iterated Coalescing (George & Appel)

- Interleave conservative coalescing with simplification so that degrees can drop and unlock more coalesces.

### Optimistic Coalescing (Park & Moon)

- Aggressively coalesce first; if a coalesced node becomes an actual spill during select, undo the coalesce and try coloring/splitting the parts separately.
- This usually reduces total spill cost because splitting a spilled merged node often allows at least one part to be colored.

### Coloring-Based Coalescing (Odaira et al.)

- Perform a *trial coloring* with extra colors; copy-related subranges that receive the same trial color are *companions* and are good coalescing candidates.
- This approach uses trial coloring to safely coalesce groups of subranges after splitting.

---

## Live-Range Splitting (Cooper & Simpson)

- Splitting a live range permits keeping values in registers for hot regions while spilling or storing them in cold regions.
- Use a containment graph to detect when one live range contains another (e.g., a loop-enclosing value) and compare the cost of splitting vs. spilling (loads + stores).

Decision example: if the split cost (added loads/stores) is less than the cost of spilling the entire range — especially when spilling would insert a load inside a hot loop — prefer splitting.

---

## Practical Notes & Experimental Results

- Optimistic and coloring-based coalescing often reduce spill code and improve runtime compared with conservative strategies; the magnitude depends on code shape and target architecture.
- Simple spill heuristics such as cost/degree remain effective and are commonly used in production allocators.

## Running the Demos

The repository contains short, self-contained Python demos in the `Implementation/` folder. Each script prints step-by-step traces for quick educational runs:

```bash
python Implementation/chaitin_coloring.py
python Implementation/linear_scan.py
python Implementation/live_range_splitting.py
python Implementation/optimistic_coalescing.py
python Implementation/coloring_based_coalescing.py
```

## References

- Chaitin, G. J. (1982). *Register Allocation & Spilling via Graph Coloring*.
- Poletto, M., & Sarkar, V. (1999). *Linear Scan Register Allocation*.
- Cooper, K. D., & Simpson, L. T. (1998). *Live Range Splitting in a Graph Coloring Register Allocator*.
- Park, J., & Moon, S. M. (2004). *Optimistic Register Coalescing*.
- Odaira, R., et al. (2010). *Coloring-Based Coalescing for Graph Coloring Register Allocation*.

For full papers see the `Research Paper/` folder and for runnable demos see the `Implementation/` folder.



--------------------------------------------------------------------------------


Foundations of Graph-Coloring Register Allocation

The Interference Graph

Register allocation abstracts the problem of assigning physical registers to "live ranges" (symbolic registers) into a vertex coloring problem.

* Nodes: Represent live ranges of variables.
* Edges: Connect two nodes if their live ranges overlap (interfere), meaning they cannot occupy the same register.
* Colors (K): Represent the finite number of available machine registers.

The Chaitin-Style Allocation Process

As established by Chaitin (1982), the allocator follows a specific sequence:

1. Renumber/Build: Identify live ranges and construct the interference graph.
2. Coalesce: Combine non-interfering source and target nodes of copy operations to eliminate the copy.
3. Simplify: Repeatedly remove "low-degree" nodes (degree < K) and push them onto a stack. A node with fewer than K neighbors is guaranteed to be colorable.
4. Spill Decision: If only "significant-degree" nodes (degree \ge K) remain, a node is chosen to be "spilled" based on a cost-benefit metric: Cost / Degree.
5. Select: Pop nodes from the stack and assign colors. If a node cannot be colored, it is "actually spilled," requiring the insertion of load/store instructions and a restart of the allocation process.


--------------------------------------------------------------------------------


The Coalescing Trade-off: Negative vs. Positive Impact

Coalescing has a dual effect on the colorability of the interference graph, a factor often overlooked in early heuristics.

Impact	Description	Consequence
Negative Impact	A coalesced node xy has a degree equal to the union of the edges of x and y.	May make a K-colorable graph non-colorable.
Positive Impact	If a neighbor z interferes with both x and y, its degree decreases by one after x and y are coalesced.	May make a non-colorable graph K-colorable by simplifying neighbor nodes.


--------------------------------------------------------------------------------


Evolution of Coalescing Heuristics

1. Aggressive Coalescing (Chaitin, 1982)

This approach coalesces any pair of non-interfering copy-related nodes.

* Pros: Maximizes copy elimination; exploits the positive impact of degree reduction.
* Cons: Totally ignores the negative impact, often leading to excessive spilling.

2. Conservative Coalescing (Briggs et al., 1994)

Coalescing is performed only if the resulting node xy has fewer than K significant-degree neighbors.

* Rationale: This ensures that coalescing never turns a colorable graph into an uncolorable one.
* Limitation: It is overly pessimistic, giving up on many coalescing opportunities that would actually turn out to be safe during the select phase.

3. Iterated Coalescing (George & Appel, 1996)

This refines conservative coalescing by interleaving it with the simplification phase. By removing low-degree non-copy-related nodes first, the degrees of copy-related nodes may drop, allowing more conservative coalesces to proceed.

4. Optimistic Coalescing (Park & Moon, 2004)

Optimistic coalescing attempts to marry the benefits of aggressive coalescing with a safety net for spills.

* The Mechanism: It aggressively coalesces nodes initially. During the Select phase, if a coalesced node xy is found to be uncolorable (an "actual spill"), the allocator undoes the coalescing.
* Splitting: The node is split back into x and y. The allocator then attempts to color x and y individually. Because x and y have lower degrees than the chunk xy, one or both may now be colorable, reducing the total spill cost.
* Experimental Result: Optimistic coalescing generates 2.5% fewer spill instructions than aggressive coalescing and significantly outperforms conservative/iterated heuristics in VLIW code scheduling.

5. Coloring-Based Coalescing (Odaira et al., 2010)

This approach uses the coloring process itself as a heuristic for coalescing.

* Trial Coloring: The allocator performs an initial "trial" coloring using an extended number of colors (> K).
* Companion Nodes: Copy-related nodes that are assigned the same color in the trial are deemed "companions."
* Rationale: If two copy-related nodes receive the same color despite interferences from their neighbors, it indicates they share a similar interference structure and are prime candidates for coalescing.
* Efficiency: This method is simpler to implement as it reuses the existing coloring function and can coalesce entire groups of nodes at once rather than just pairs.


--------------------------------------------------------------------------------


Performance Analysis and Experimental Data

Comparison of Heuristics

The effectiveness of these heuristics varies based on the environment (e.g., SPECjvm98 benchmarks for Java or EPS scheduling for VLIW).

Spill Instruction Reduction (Normalized to Chaitin's Base-Case):

* Conservative: ~88% of base-case spills.
* Iterated: ~86% of base-case spills.
* Aggressive: ~76% of base-case spills.
* Optimistic: ~74% of base-case spills.
* Optimistic+ (Extended): ~73% of base-case spills.

Java Benchmark Results (16 Registers): Coloring-based coalescing combined with live-range splitting showed a significant reduction in static spill costs compared to the baseline (no splitting):

* Coloring-based (Twice): 6% reduction.
* Coloring-based (3 Times): 18% reduction.
* Iterated/Optimistic with Splitting: Increased costs by >20% in some instances due to over-aggressive or poorly timed decisions.

Impact on Execution Time

In high-pressure register environments (e.g., _222_mpegaudio), advanced coalescing significantly impacts performance:

* Coloring-Based Coalescing: Average 3% speed-up; up to 15% maximum.
* Optimistic Coalescing: Average 3.5% speed-up in VLIW environments.


--------------------------------------------------------------------------------


Advanced Issues in Register Allocation

Live Range Splitting

Live range splitting inserts copies to break long live ranges into smaller "sub-ranges," allowing the allocator to spill only the parts of a variable that are under high pressure.

* The Problem: Splitting generates excessive copies.
* The Solution: Optimistic or Coloring-based coalescing acts as a "cleanup pass," merging sub-ranges back together where possible while retaining the benefits of the split where pressure remains high.

Precoloring

Certain variables (like function parameters) must reside in specific physical registers.

* Challenges: Precolored nodes have "infinite" spill costs. Coalescing a normal node with a precolored node can make the graph uncolorable.
* Optimistic Approach: Park and Moon suggest "virtual" coalescing for precolored nodes—adding interference edges rather than physical merging—to allow the coalesce to be "undone" during the select phase if it causes a spill.

Algorithm Complexity

While many of these heuristics involve iterative processes, their practical overhead remains manageable.

* Optimistic Coalescing: The "undo" test for colorable splits is theoretically exponential (O(2^n)), but since the average number of primitive nodes in a coalesced chunk is low (2.2), it remains fast.
* Coloring-Based Coalescing: The temporal complexity is primarily driven by performing the coloring algorithm twice, which Java JIT compiler experiments suggest is a negligible trade-off for the resulting 3%–15% performance gains.
