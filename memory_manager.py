class PhysicalMemory:
    def __init__(self, num_frames=32):
        self.num_frames = num_frames
        # Each frame stores (process_id, virtual_page_num) or None if free
        self.frames = [None] * num_frames
        
    def find_free_frame(self):
        for i, frame in enumerate(self.frames):
            if frame is None:
                return i
        return None
    
    def allocate_frame(self, frame_num, process_id, virtual_page_num):
        self.frames[frame_num] = (process_id, virtual_page_num)
    
    def free_frame(self, frame_num):
        self.frames[frame_num] = None
    
    def get_frame_info(self, frame_num):
        return self.frames[frame_num]
    
    def is_full(self):
        return self.find_free_frame() is None


class Statistics:
    def __init__(self):
        self.page_faults = 0
        self.disk_accesses = 0
        self.dirty_writes = 0
        
    def record_page_fault(self, is_dirty_replacement=False):
        self.page_faults += 1
        if is_dirty_replacement:
            # Dirty page: write back + read new page
            self.disk_accesses += 2
            self.dirty_writes += 1
        else:
            # Clean page: just read new page
            self.disk_accesses += 1
    
    def __str__(self):
        return (f"Page Faults: {self.page_faults}\n"
                f"Disk Accesses: {self.disk_accesses}\n"
                f"Dirty Writes: {self.dirty_writes}")
