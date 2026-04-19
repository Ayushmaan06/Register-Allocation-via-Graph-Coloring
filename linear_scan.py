"""Poletto & Sarkar (1999) demo: linear scan register allocation.

This script runs linear scan on hardcoded live intervals with R=3 registers,
showing expire and spill decisions step by step.
"""

from dataclasses import dataclass


@dataclass
class Interval:
    name: str
    start: int
    end: int
    reg: str = ""


def active_str(active):
    if not active:
        return "[]"
    body = ", ".join(f"{iv.name}[{iv.start},{iv.end}]={iv.reg}" for iv in active)
    return f"[{body}]"


def expireOldIntervals(current, active, free_registers):
    print(f"  Active before expire: {active_str(active)}")
    kept = []
    for iv in sorted(active, key=lambda x: x.end):
        if iv.end < current.start:
            free_registers.append(iv.reg)
            print(f"  Expire {iv.name}: release {iv.reg} (end={iv.end} < start={current.start})")
        else:
            kept.append(iv)
    active[:] = sorted(kept, key=lambda x: x.end)
    free_registers.sort()
    print(f"  Active after expire:  {active_str(active)}")


def spillAtInterval(current, active, assignment):
    print("  === spillAtInterval() ===")
    print(f"  Before spill decision: {active_str(active)}")
    spill = active[-1]  # longest-remaining interval (largest end)
    print(
        f"  Compare current {current.name}[{current.start},{current.end}] "
        f"with longest active {spill.name}[{spill.start},{spill.end}]"
    )

    if spill.end > current.end:
        current.reg = spill.reg
        assignment[spill.name] = "SPILL"
        assignment[current.name] = current.reg
        active[-1] = current
        active.sort(key=lambda x: x.end)
        print(f"  Spill active {spill.name}, reuse {current.reg} for {current.name}")
    else:
        assignment[current.name] = "SPILL"
        print(f"  Spill current {current.name} (longest active survives)")

    print(f"  After spill decision:  {active_str(active)}")


def linearScan(intervals, R):
    registers = [f"R{i}" for i in range(R)]
    free_registers = registers.copy()
    active = []
    assignment = {}

    print("=== LINEAR SCAN PHASE ===")
    for current in sorted(intervals, key=lambda x: x.start):
        print(f"\nProcess interval {current.name}[{current.start},{current.end}]")
        print(f"  Free registers at start: {free_registers}")
        expireOldIntervals(current, active, free_registers)

        if free_registers:
            reg = free_registers.pop(0)
            current.reg = reg
            assignment[current.name] = reg
            active.append(current)
            active.sort(key=lambda x: x.end)
            print(f"  Assign {current.name} -> {reg}")
        else:
            spillAtInterval(current, active, assignment)

        print(f"  Active now: {active_str(active)}")
        print(f"  Free now:   {free_registers}")

    return assignment


def main():
    intervals = [
        Interval("A", 0, 9),
        Interval("B", 1, 4),
        Interval("C", 2, 7),
        Interval("D", 3, 5),
        Interval("E", 6, 10),
        Interval("F", 8, 11),
        Interval("G", 9, 12),
        Interval("H", 10, 13),
    ]

    result = linearScan(intervals, R=3)

    print("\n=== RESULT ===")
    for iv in sorted(intervals, key=lambda x: x.name):
        print(f"{iv.name} -> {result.get(iv.name, 'SPILL')}")


if __name__ == "__main__":
    main()
