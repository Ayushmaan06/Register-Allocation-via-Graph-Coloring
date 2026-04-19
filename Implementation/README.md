# Implementation

This directory contains Python demonstrations of the core algorithms from each research paper. Each script is a self-contained simulation, using hardcoded examples to illustrate the paper's key ideas.

## Scripts Included

1. **chaitin_coloring.py** - Implements Chaitin's (1982) simplify/select allocation.  
   Simulates graph coloring on small interference graphs, showing spill decisions and cost calculations.

2. **linear_scan.py** - Implements Poletto & Sarkar's (1999) linear scan.  
   Demonstrates interval-based allocation with expire and spill-at-interval logic.

3. **live_range_splitting.py** - Implements Cooper & Simpson's (1998) split-vs-spill decision.  
   Uses containment graphs to compare spilling a live range entirely vs. splitting it around interfering ranges.

4. **optimistic_coalescing.py** - Implements Park & Moon's (2004) optimistic coalescing.  
   Shows aggressive coalescing followed by undo when merged nodes are uncolorable, reducing spills.

5. **coloring_based_coalescing.py** - Implements Odaira et al.'s (2010) coloring-based coalescing.  
   Performs trial coloring to identify companions for coalescing after live range splitting.

## Running the Scripts

Each file runs independently with:
```bash
python filename.py
```

They print step-by-step traces, final assignments, and comparisons (e.g., spill counts), designed for graduate-level understanding in 2-3 minutes.

## Requirements

- Python 3.x
- No external libraries (pure Python)

## Educational Focus

These demos simulate only the register allocation phase, not full compilation. They highlight trade-offs like copy elimination vs. spill minimization, using small examples for clarity.

For the original papers, see `../Research Paper/`. For detailed background, see `../summary.md`.