class PageTableEntry:
    def __init__(self, virtual_page_num):
        self.virtual_page_num = virtual_page_num
        self.physical_page_num = None  # None means not in memory
        self.dirty = False
        self.reference = False
        self.last_access_time = 0
        self.load_time = 0  # For FIFO
        self.access_count = 0  # For LFU
        
    def is_valid(self):
        return self.physical_page_num is not None


class PageTable:
    def __init__(self, process_id, num_pages=128):
        self.process_id = process_id
        self.entries = [PageTableEntry(i) for i in range(num_pages)]
        
    def get_entry(self, virtual_page_num):
        return self.entries[virtual_page_num]
    
    def reset_reference_bits(self):
        for entry in self.entries:
            entry.reference = False
