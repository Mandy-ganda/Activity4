"""Programming works: a queue (FIFO) built on linked nodes."""


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class Queue:
    """First In, First Out. Items enter at the rear and leave from the front."""

    def __init__(self, capacity=10):
        self.front = None
        self.rear = None
        self._size = 0
        self.capacity = capacity

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def is_full(self):
        return self._size >= self.capacity

    def enqueue(self, value):
        if self.is_full():
            raise OverflowError(f"Queue is full (maximum {self.capacity} items).")
        node = Node(value)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty, nothing to dequeue.")
        value = self.front.value
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self._size -= 1
        return value

    def peek(self):
        if self.is_empty():
            raise IndexError("Queue is empty, nothing at the front.")
        return self.front.value

    def clear(self):
        self.front = self.rear = None
        self._size = 0

    def to_list(self):
        items, cur = [], self.front
        while cur:
            items.append(cur.value)
            cur = cur.next
        return items
