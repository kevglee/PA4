from page_table import PageTable
from memory_manager import PhysicalMemory, Statistics
from simulator import VirtualMemorySimulator

def test_small():
    print("Testing with test.txt")
    print("Input file contents:")
    with open('test.txt', 'r') as f:
        for i, line in enumerate(f, 1):
            print(f"  Line {i}: {line.strip()}")

    algorithms = ['RAND', 'FIFO', 'LRU', 'PER', 'LFU']
    
    for algorithm in algorithms:
        print(f"\n{algorithm} Algorithm:")
        print("-"*60)
        simulator = VirtualMemorySimulator(algorithm=algorithm, random_seed=None)
        stats = simulator.run_simulation('test.txt')
        
if __name__ == '__main__':
    test_small()
