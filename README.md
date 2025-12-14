# PA4 - Virtual Memory Simulator
COMPE 571 Programming Assignment 4

## Overview

This project simulates a virtual memory system with four page replacement algorithms.

## Files

- `simulator.py` - Main simulation program
- `page_table.py` - Page table implementation
- `memory_manager.py` - Physical memory and statistics tracking
- `generate_graphs.py` - Creates comparison graphs
- `test_small.py` - Small test verification
- `data1.txt`, `data2.txt` - Input data files
- `test.txt` - Small test input file

## Running the Simulator

Running all four algorithms on both input files:

```bash
python simulator.py
```

This will execute:
- **RAND** - Random replacement with seed 42
- **FIFO** - First In First Out
- **LRU** - Least Recently Used
- **PER** - Periodic reference reset

on both `data1.txt` and `data2.txt`, displaying statistics for each run.

## Testing

Verifying the simulator with a small test case:

```bash
python test_small.py
```

This runs all algorithms on `test.txt` (10 memory references).

## Generating Graphs

Installing matplotlib to create graphs:

```bash
pip install matplotlib
```

Creating comparison graphs:

```bash
python generate_graphs.py
```

This produces `algorithm_comparison.png` with three charts comparing page faults, disk accesses, and dirty page writes across all algorithms.

