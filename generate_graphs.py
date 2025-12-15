import matplotlib.pyplot as plt
from simulator import VirtualMemorySimulator

algorithms = ['RAND', 'FIFO', 'LRU', 'PER', 'LFU']
data_files = ['data1.txt', 'data2.txt']
results = {}

print("Running simulations...")
for data_file in data_files:
    results[data_file] = {}
    for algorithm in algorithms:
        simulator = VirtualMemorySimulator(algorithm=algorithm, random_seed=None)
        stats = simulator.run_simulation(data_file)
        results[data_file][algorithm] = {
            'page_faults': stats.page_faults,
            'disk_accesses': stats.disk_accesses,
            'dirty_writes': stats.dirty_writes
        }

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Page Replacement Algorithm Comparison', fontsize=14, fontweight='bold')

metrics = ['page_faults', 'disk_accesses', 'dirty_writes']
titles = ['Page Faults', 'Disk Accesses', 'Dirty Page Writes']

legend_handles = None

for idx, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[idx]
    data1 = [results['data1.txt'][alg][metric] for alg in algorithms]
    data2 = [results['data2.txt'][alg][metric] for alg in algorithms]
    
    x = range(len(algorithms))
    width = 0.35
    bars1 = ax.bar([i - width/2 for i in x], data1, width, label='data1.txt')
    bars2 = ax.bar([i + width/2 for i in x], data2, width, label='data2.txt')
    
    if idx == 0:
        legend_handles = [bars1[0], bars2[0]]
    
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.grid(axis='y', alpha=0.3)

fig.legend(legend_handles, ['data1.txt', 'data2.txt'], loc='lower center', ncol=2, frameon=True)

plt.tight_layout()
plt.subplots_adjust(bottom=0.1)
plt.savefig('algorithm_comparison.png', dpi=300, bbox_inches='tight')
print("\nGraph saved as 'algorithm_comparison.png'")
plt.show()
