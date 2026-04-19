# Register Allocation via Graph Coloring

This repository explores the evolution of register allocation techniques, focusing on graph-coloring approaches and advanced coalescing heuristics. Register allocation is a critical compiler optimization that assigns physical registers to program variables, minimizing memory accesses (spills) while respecting interference constraints.

## Overview

Global register allocation models the problem as a graph coloring task:
- **Nodes**: Represent live ranges of variables.
- **Edges**: Indicate interference (overlapping lifetimes).
- **Colors**: Correspond to available machine registers (K).

The repository demonstrates key algorithms from seminal research papers, implemented as educational Python simulations. These scripts simulate core mechanisms without full compiler infrastructure, highlighting trade-offs between copy elimination and spill minimization.

## Repository Structure

- **[Research Paper](./Research%20Paper/)**: Original research papers in PDF format.
- **[Implementation](./Implementation/)**: Python demonstrations of each paper's algorithm.
- **[Presentation and Report](./Presentation%20and%20Report/)**: Slides, reports, and documentation.

## Key Concepts Covered

### Foundations (Chaitin, 1982)
- Interference graph construction.
- Simplify/select phases with spill heuristics.

### Linear Scan (Poletto & Sarkar, 1999)
- Fast, linear-time allocation for JIT compilers.
- Expire intervals and spill-at-interval decisions.

### Live Range Splitting (Cooper & Simpson, 1998)
- Split-vs-spill trade-offs in graph coloring.
- Containment graphs and cost comparisons.

### Optimistic Coalescing (Park & Moon, 2004)
- Aggressive coalescing with undo mechanism.
- Reduces spills by splitting uncolorable merged nodes.

### Coloring-Based Coalescing (Odaira et al., 2010)
- Trial coloring identifies "companions" for safe coalescing.
- Post-splitting interference graph optimization.

## Running the Implementations

Each Python script in `Implementation/` is self-contained and runs with:
```bash
python filename.py
```

They use hardcoded examples to illustrate algorithm behavior, printing step-by-step traces for educational purposes.

## References

- Chaitin, G. J. (1982). Register Allocation & Spilling via Graph Coloring.
- Poletto, M., & Sarkar, V. (1999). Linear Scan Register Allocation.
- Cooper, K. D., & Simpson, L. T. (1998). Live Range Splitting in a Graph Coloring Register Allocator.
- Park, J., & Moon, S. M. (2004). Optimistic Register Coalescing.
- Odaira, R., et al. (2010). Coloring-Based Coalescing for Graph Coloring Register Allocation.

For detailed analysis, see [summary.md](./summary.md).