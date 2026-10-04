"""Programming works: a singly linked list."""


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    def __len__(self):
        return self._size

    def to_list(self):
        items, cur = [], self.head
        while cur:
            items.append(cur.value)
            cur = cur.next
        return items

    def append(self, value):
        node = Node(value)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._size += 1
        return self._size - 1

    def prepend(self, value):
        node = Node(value)
        node.next = self.head
        self.head = node
        self._size += 1
        return 0

    def insert(self, index, value):
        if index < 0 or index > self._size:
            raise IndexError(f"Index must be between 0 and {self._size}.")
        if index == 0:
            return self.prepend(value)
        prev = self.head
        for _ in range(index - 1):
            prev = prev.next
        node = Node(value)
        node.next = prev.next
        prev.next = node
        self._size += 1
        return index

    def find(self, value):
        cur, i = self.head, 0
        while cur:
            if cur.value.lower() == value.lower():
                return i
            cur, i = cur.next, i + 1
        return -1

    def remove_at(self, index):
        if index < 0 or index >= self._size:
            raise IndexError("That index is not in the list.")
        if index == 0:
            removed = self.head.value
            self.head = self.head.next
        else:
            prev = self.head
            for _ in range(index - 1):
                prev = prev.next
            removed = prev.next.value
            prev.next = prev.next.next
        self._size -= 1
        return removed

    def remove(self, value):
        index = self.find(value)
        if index == -1:
            raise ValueError(f'"{value}" is not in the list.')
        self.remove_at(index)
        return index

    def reverse(self):
        prev, cur = None, self.head
        while cur:
            cur.next, prev, cur = prev, cur, cur.next
        self.head = prev

    def clear(self):
        self.head = None
        self._size = 0
