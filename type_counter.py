from __future__ import annotations

from typing import Optional


class TypeCounterNode:
    __slots__ = ("record_type", "count", "next")

    def __init__(self, record_type: str, count: int = 0, next_node: Optional["TypeCounterNode"] = None):
        self.record_type = record_type
        self.count = count
        self.next = next_node


class TypeCounter:
    def __init__(self):
        self._head: Optional[TypeCounterNode] = None

    def _find_node(self, record_type: str) -> Optional[TypeCounterNode]:
        current = self._head
        while current is not None:
            if current.record_type == record_type:
                return current
            current = current.next
        return None

    def increment(self, record_type: str) -> None:
        node = self._find_node(record_type)
        if node is None:
            self._head = TypeCounterNode(record_type, 1, self._head)
        else:
            node.count += 1

    def decrement(self, record_type: str) -> None:
        current = self._head
        previous = None

        while current is not None:
            if current.record_type == record_type:
                current.count -= 1

                if current.count <= 0:
                    if previous is None:
                        self._head = current.next
                    else:
                        previous.next = current.next
                return

            previous = current
            current = current.next

    def clear(self) -> None:
        self._head = None

    def items(self) -> list[tuple[str, int]]:
        result: list[tuple[str, int]] = []
        current = self._head
        while current is not None:
            result.append((current.record_type, current.count))
            current = current.next
        result.sort(key=lambda x: x[0])
        return result
