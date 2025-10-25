class DqNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class Deque:
    def __init__(self, datos=None):
        self._head = None
        self._tail = None
        self._size = 0
        if datos is not None:
            try:
                for x in datos:
                    self.push_back(x)
            except TypeError:
                self.push_back(datos)

    def push_front(self, x):
        n = DqNode(x)
        if self._head is None:
            self._head = self._tail = n
        else:
            n.next = self._head
            self._head.prev = n
            self._head = n
        self._size += 1

    def push_back(self, x):
        n = DqNode(x)
        if self._tail is None:
            self._head = self._tail = n
        else:
            n.prev = self._tail
            self._tail.next = n
            self._tail = n
        self._size += 1

    def pop_front(self):
        if self._head is None:
            return None
        n = self._head
        val = n.data
        self._head = n.next
        if self._head is None:
            self._tail = None
        else:
            self._head.prev = None
        self._size -= 1
        return val

    def pop_back(self):
        if self._tail is None:
            return None
        n = self._tail
        val = n.data
        self._tail = n.prev
        if self._tail is None:
            self._head = None
        else:
            self._tail.next = None
        self._size -= 1
        return val

    def front(self):
        return None if self._head is None else self._head.data

    def back(self):
        return None if self._tail is None else self._tail.data

    def empty(self):
        return self._size == 0

    def count(self):
        return self._size

    def clear(self):
        i = self._head
        while i is not None:
            nxt = i.next
            i.prev = None
            i.next = None
            i = nxt
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        i = self._head
        while i is not None:
            yield i.data
            i = i.next

    def __repr__(self):
        return f"Deque(size={self._size})"

