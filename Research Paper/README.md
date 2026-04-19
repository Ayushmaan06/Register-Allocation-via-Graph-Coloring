# Research Paper

This directory contains the original research papers that form the foundation of the register allocation implementations in this repository. Each paper introduces key innovations in graph-coloring register allocation and coalescing heuristics.

## Papers Included

1. **chaitin82.pdf** - Chaitin, G. J. (1982). *Register Allocation & Spilling via Graph Coloring*.  
   Introduces the core graph-coloring framework for register allocation, including simplify/select phases and spill cost heuristics.

2. **linearscan.pdf** - Poletto, M., & Sarkar, V. (1999). *Linear Scan Register Allocation*.  
   Presents a fast, linear-time alternative to graph coloring, suitable for JIT compilers, with interval-based allocation.

3. **live-range-splitting.pdf** - Cooper, K. D., & Simpson, L. T. (1998). *Live Range Splitting in a Graph Coloring Register Allocator*.  
   Explores splitting live ranges to avoid spills, using containment graphs to compare split-vs-spill costs.

4. **1011508.1011512.pdf** - Park, J., & Moon, S. M. (2004). *Optimistic Register Coalescing*.  
   Proposes aggressive coalescing with an undo mechanism to reduce spills by splitting uncolorable merged nodes.

5. **1772954.1772978.pdf** - Odaira, R., et al. (2010). *Coloring-Based Coalescing for Graph Coloring Register Allocation*.  
   Uses trial coloring to identify "companion" nodes for safe coalescing after live range splitting.

## Usage

These PDFs provide the theoretical background for the Python implementations in the `../Implementation/` directory. Read them to understand the algorithms before running the demos.

For a comprehensive summary of the coalescing evolution, see `../summary.md`.