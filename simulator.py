from page_table import PageTable
from memory_manager import PhysicalMemory, Statistics
import random


class VirtualMemorySimulator:
    
    def __init__(self, algorithm='FIFO', random_seed=None):
        self.algorithm = algorithm
        self.physical_memory = PhysicalMemory(num_frames=32)
        self.page_tables = {}  # process_id -> PageTable
        self.stats = Statistics()
        self.current_time = 0
        
        # Set random seed for RAND algorithm
        if algorithm == 'RAND':
            if random_seed is None:
                import time
                random.seed(int(time.time() * 1000000) % (2**31))
            else:
                random.seed(random_seed)
        
    def parse_address(self, address):
        page_num = address >> 9  # Upper 7 bits
        offset = address & 0x1FF  # Lower 9 bits (0x1FF = 511)
        return page_num, offset
    
    def get_page_table(self, process_id):
        if process_id not in self.page_tables:
            self.page_tables[process_id] = PageTable(process_id)
        return self.page_tables[process_id]
    
    def handle_memory_reference(self, process_id, address, operation):
        self.current_time += 1
        
        # Parse address
        page_num, offset = self.parse_address(address)
        
        # Get page table and entry
        page_table = self.get_page_table(process_id)
        entry = page_table.get_entry(page_num)
        
        # Update reference bit and last access time
        entry.reference = True
        entry.last_access_time = self.current_time
        entry.access_count += 1
        
        # Check if page is in memory
        if entry.is_valid():
            # Page hit - just update dirty bit if write
            if operation == 'W':
                entry.dirty = True
        else:
            # Page fault
            self.handle_page_fault(process_id, page_num, operation)
        
        # For PER algorithm: reset reference bits every 200 references
        if self.algorithm == 'PER' and self.current_time % 200 == 0:
            for pt in self.page_tables.values():
                pt.reset_reference_bits()
    
    def handle_page_fault(self, process_id, page_num, operation):
        page_table = self.get_page_table(process_id)
        entry = page_table.get_entry(page_num)
        
        frame_num = self.physical_memory.find_free_frame()
        
        if frame_num is None:
            frame_num, is_dirty = self.select_victim_page()
            self.stats.record_page_fault(is_dirty_replacement=is_dirty)
        else:
            # Free frame available
            self.stats.record_page_fault(is_dirty_replacement=False)
        
        self.physical_memory.allocate_frame(frame_num, process_id, page_num)
        entry.physical_page_num = frame_num
        entry.load_time = self.current_time
        
        if operation == 'W':
            entry.dirty = True
    
    def select_victim_page(self):
        if self.algorithm == 'RAND':
            return self.select_victim_random()
        elif self.algorithm == 'FIFO':
            return self.select_victim_fifo()
        elif self.algorithm == 'LRU':
            return self.select_victim_lru()
        elif self.algorithm == 'PER':
            return self.select_victim_per()
        elif self.algorithm == 'LFU':
            return self.select_victim_lfu()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
    
    def select_victim_random(self):
        frame_num = random.randint(0, self.physical_memory.num_frames - 1)
        return self.evict_page(frame_num)
    
    def select_victim_fifo(self):
        oldest_time = float('inf')
        victim_frame = 0
        
        for frame_num in range(self.physical_memory.num_frames):
            proc_id, vpage_num = self.physical_memory.get_frame_info(frame_num)
            page_table = self.page_tables[proc_id]
            entry = page_table.get_entry(vpage_num)
            
            if entry.load_time < oldest_time:
                oldest_time = entry.load_time
                victim_frame = frame_num
        
        return self.evict_page(victim_frame)
    
    def select_victim_lru(self):
        lru_time = float('inf')
        victim_frame = 0
        victim_dirty = True
        victim_page_num = float('inf')
        
        for frame_num in range(self.physical_memory.num_frames):
            proc_id, vpage_num = self.physical_memory.get_frame_info(frame_num)
            page_table = self.page_tables[proc_id]
            entry = page_table.get_entry(vpage_num)
            
            # If same LRU time, prefer non-dirty, then lower page number
            if entry.last_access_time < lru_time:
                lru_time = entry.last_access_time
                victim_frame = frame_num
                victim_dirty = entry.dirty
                victim_page_num = vpage_num
            elif entry.last_access_time == lru_time:
                # Same time - tiebreaker rules
                if not entry.dirty and victim_dirty:
                    # Prefer non-dirty
                    victim_frame = frame_num
                    victim_dirty = entry.dirty
                    victim_page_num = vpage_num
                elif entry.dirty == victim_dirty and vpage_num < victim_page_num:
                    # Same dirty status - prefer lower page number
                    victim_frame = frame_num
                    victim_dirty = entry.dirty
                    victim_page_num = vpage_num
        
        return self.evict_page(victim_frame)
    
    def select_victim_lfu(self):
        # First pass: find the oldest access time (like LRU)
        oldest_time = float('inf')
        candidates = []  # Pages with oldest access times
        
        for frame_num in range(self.physical_memory.num_frames):
            proc_id, vpage_num = self.physical_memory.get_frame_info(frame_num)
            page_table = self.page_tables[proc_id]
            entry = page_table.get_entry(vpage_num)
            
            if entry.last_access_time < oldest_time:
                oldest_time = entry.last_access_time
                candidates = [(frame_num, entry, proc_id, vpage_num)]
            elif entry.last_access_time == oldest_time:
                candidates.append((frame_num, entry, proc_id, vpage_num))

        RECENCY_WINDOW = 10  # Similar recency
        

        if len(candidates) == 1:
            # Check if other pages are within the window
            for frame_num in range(self.physical_memory.num_frames):
                proc_id, vpage_num = self.physical_memory.get_frame_info(frame_num)
                page_table = self.page_tables[proc_id]
                entry = page_table.get_entry(vpage_num)
                
                if entry.last_access_time <= oldest_time + RECENCY_WINDOW:
                    if (frame_num, entry, proc_id, vpage_num) not in candidates:
                        candidates.append((frame_num, entry, proc_id, vpage_num))
        
        victim_frame = candidates[0][0]
        victim_entry = candidates[0][1]
        victim_dirty = victim_entry.dirty
        victim_page_num = candidates[0][3]
        min_frequency = victim_entry.access_count
        
        for frame_num, entry, proc_id, vpage_num in candidates[1:]:
            if entry.access_count < min_frequency:
                victim_frame = frame_num
                victim_entry = entry
                victim_dirty = entry.dirty
                victim_page_num = vpage_num
                min_frequency = entry.access_count
            elif entry.access_count == min_frequency:
                # Same frequency - prefer non-dirty, then lower page number
                if not entry.dirty and victim_dirty:
                    victim_frame = frame_num
                    victim_entry = entry
                    victim_dirty = entry.dirty
                    victim_page_num = vpage_num
                elif entry.dirty == victim_dirty and vpage_num < victim_page_num:
                    victim_frame = frame_num
                    victim_entry = entry
                    victim_dirty = entry.dirty
                    victim_page_num = vpage_num
        
        return self.evict_page(victim_frame)
    
    def select_victim_per(self):
        categories = [
            (False, False),  # unreferenced, clean
            (False, True),   # unreferenced, dirty
            (True, False),   # referenced, clean
            (True, True)     # referenced, dirty
        ]
        
        for ref_bit, dirty_bit in categories:
            candidates = []
            
            for frame_num in range(self.physical_memory.num_frames):
                proc_id, vpage_num = self.physical_memory.get_frame_info(frame_num)
                page_table = self.page_tables[proc_id]
                entry = page_table.get_entry(vpage_num)
                
                if entry.reference == ref_bit and entry.dirty == dirty_bit:
                    candidates.append((frame_num, vpage_num))
            
            if candidates:
                # Always replace the lowest numbered page
                victim_frame = min(candidates, key=lambda x: x[1])[0]
                return self.evict_page(victim_frame)
        
        return self.evict_page(0)
    
    def evict_page(self, frame_num):
        proc_id, vpage_num = self.physical_memory.get_frame_info(frame_num)
        page_table = self.page_tables[proc_id]
        entry = page_table.get_entry(vpage_num)
        
        is_dirty = entry.dirty
        
        # Clear the page table entry
        entry.physical_page_num = None
        entry.dirty = False
        entry.reference = False
        entry.access_count = 0  # Reset access count for LFU
        
        return frame_num, is_dirty
    
    def run_simulation(self, filename):
        print(f"\n{'='*60}")
        print(f"Running {self.algorithm} algorithm on {filename}")
        print(f"{'='*60}")
        
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue
                
                process_id = int(parts[0])
                address = int(parts[1])
                operation = parts[2]
                
                self.handle_memory_reference(process_id, address, operation)
        
        print(f"\nResults:")
        print(self.stats)
        print(f"{'='*60}\n")
        
        return self.stats


def main():
    algorithms = ['RAND', 'FIFO', 'LRU', 'PER', 'LFU']
    data_files = ['data1.txt', 'data2.txt']
    
    results = {}
    
    for data_file in data_files:
        results[data_file] = {}
        print(f"\n{'#'*60}")
        print(f"# Processing {data_file}")
        print(f"{'#'*60}")
        
        for algorithm in algorithms:
            simulator = VirtualMemorySimulator(algorithm=algorithm, random_seed=None)
            stats = simulator.run_simulation(data_file)
            results[data_file][algorithm] = {
                'page_faults': stats.page_faults,
                'disk_accesses': stats.disk_accesses,
                'dirty_writes': stats.dirty_writes
            }
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY OF ALL RESULTS")
    print("="*80)
    
    for data_file in data_files:
        print(f"\n{data_file}:")
        print(f"{'Algorithm':<10} {'Page Faults':<15} {'Disk Accesses':<15} {'Dirty Writes':<15}")
        print("-" * 60)
        for algorithm in algorithms:
            r = results[data_file][algorithm]
            print(f"{algorithm:<10} {r['page_faults']:<15} {r['disk_accesses']:<15} {r['dirty_writes']:<15}")


if __name__ == '__main__':
    main()
