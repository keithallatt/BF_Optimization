# -*- coding: utf-8 -*-
"""
Brainfuck with additional things such as memory allocation.
"""

# str: null terminated
# int: 1 cell


class BFMemory:
    def __init__(self, bank_size):
        self.bank_size = bank_size
        self.mapping_name2memory = {}
        self.mapping_memory2name = {}
        self.allocated = set()

    def _allocate_memory(self, size=1):
        """
        Allocate $size$ contiguous bytes of memory and return the addresses allocated.
        """
        allocated_memory = sorted(list(self.allocated))
        for i in range(1, len(allocated_memory)):
            difference = allocated_memory[i] - allocated_memory[i-1]
            if difference > size:
                return allocated_memory[i-1] + 1
        else:
            return max([-1] + allocated_memory) + 1

    def allocate_named_variable(self, name: str, size: int = 1):
        """
        Allocate memory for a named object (non-temporary)
        """
        memory_address = self._allocate_memory(size)
        self.mapping_name2memory[name] = (memory_address, memory_address + size - 1)
        self.mapping_memory2name[memory_address] = name

    def free_named_variable(self, name):
        assert name in self.mapping_name2memory.keys(), "Attempting to free non-existing variable."
        addresses = self.mapping_name2memory[name]
        # print(addresses)

    def change_memory_address(self, old, new):
        """
        Move data in one cell to another to either defragment the memory or to make room for
        a new allocation.
        """
        pass


if __name__ == "__main__":
    bfm = BFMemory(128)
    bfm.allocate_named_variable("foo", size=3)
    # print(bfm.mapping_name2memory)

    bfm.free_named_variable("foo")

    # print(bfm.mapping_name2memory)
