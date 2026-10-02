from __future__ import annotations
from typing import Callable, Iterator, Optional
from dns_record import DNSRecord


class HashNode:
    __slots__ = ("key", "record", "next")
    def __init__(self, key: str, record: DNSRecord, next_node: Optional["HashNode"] = None):
        self.key = key
        self.record = record
        self.next = next_node


class HashTable:
 
    def __init__(self, initial_capacity: int = 1024, max_load_factor: float = 0.75):
        if initial_capacity < 4:
            initial_capacity = 4
        self._capacity = initial_capacity
        self._buckets: list[Optional[HashNode]] = [None] * self._capacity
        self._size = 0
        self._max_load_factor = max_load_factor

    @property
    def size(self) -> int:
        return self._size

    @property
    def capacity(self) -> int:
        return self._capacity

    def _hash(self, key: str) -> int:
        h = 0
        p = 53
        mod = 2_147_483_647
        for ch in key:
            h = (h * p + ord(ch)) % mod
        return h

    def _index(self, key: str) -> int:
        return self._hash(key) % self._capacity

    def _need_resize(self) -> bool:
        return self._size / self._capacity > self._max_load_factor

    def _resize(self) -> None:
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        old_size = self._size
        self._size = 0

        for head in old_buckets:
            current = head
            while current is not None:
                next_node = current.next
                current.next = None
                self._insert_existing_node(current)
                current = next_node

        self._size = old_size

    def _insert_existing_node(self, node: HashNode) -> None:
        idx = self._index(node.key)
        node.next = self._buckets[idx]
        self._buckets[idx] = node

    def put(self, key: str, record: DNSRecord) -> bool:
        idx = self._index(key)
        current = self._buckets[idx]

        while current is not None:
            if current.key == key:
                current.record = record
                return False
            current = current.next

        self._buckets[idx] = HashNode(key, record, self._buckets[idx])
        self._size += 1

        if self._need_resize():
            self._resize()

        return True

    def get(self, key: str) -> Optional[DNSRecord]:
        idx = self._index(key)
        current = self._buckets[idx]

        while current is not None:
            if current.key == key:
                return current.record
            current = current.next

        return None

    def delete(self, key: str) -> Optional[DNSRecord]:
        idx = self._index(key)
        current = self._buckets[idx]
        previous = None

        while current is not None:
            if current.key == key:
                if previous is None:
                    self._buckets[idx] = current.next
                else:
                    previous.next = current.next
                self._size -= 1
                return current.record

            previous = current
            current = current.next

        return None

    def update(self, key: str, update_func: Callable[[DNSRecord], None]) -> bool:
        record = self.get(key)
        if record is None:
            return False
        update_func(record)
        return True

    def remove_if(self, predicate: Callable[[DNSRecord], bool]) -> list[DNSRecord]:
        removed: list[DNSRecord] = []

        for i in range(self._capacity):
            current = self._buckets[i]
            previous = None

            while current is not None:
                if predicate(current.record):
                    removed.append(current.record)

                    if previous is None:
                        self._buckets[i] = current.next
                        current = self._buckets[i]
                    else:
                        previous.next = current.next
                        current = previous.next

                    self._size -= 1
                else:
                    previous = current
                    current = current.next

        return removed

    def records(self) -> Iterator[DNSRecord]:
        for head in self._buckets:
            current = head
            while current is not None:
                yield current.record
                current = current.next
