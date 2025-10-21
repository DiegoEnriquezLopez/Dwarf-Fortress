from doubly_linked_list import DoublyLinkedList

class Deque:
    def __init__(self, datos=None):
        self._dll = DoublyLinkedList()
        self._shadow = {}
        self._left = 0
        self._right = -1
        if datos is not None:
            try:
                for d in datos:
                    self.push_back(d)
            except TypeError:
                self.push_back(datos)

    def push_front(self, x):
        self._dll.preppend(x)
        self._left -= 1
        self._shadow[self._left] = x

    def push_back(self, x):
        self._dll.append(x)
        self._right += 1
        self._shadow[self._right] = x

    def pop_front(self):
        if self.empty():
            return None
        val = self._shadow.pop(self._left, None)
        self._dll.remove(index=0)
        self._left += 1
        return val

    def pop_back(self):
        if self.empty():
            return None
        val = self._shadow.pop(self._right, None)
        last_idx = len(self._dll) - 1
        self._dll.remove(index=last_idx)
        self._right -= 1
        return val

    def front(self):
        if self.empty():
            return None
        return self._shadow.get(self._left, None)

    def back(self):
        if self.empty():
            return None
        return self._shadow.get(self._right, None)

    def empty(self):
        return self._dll.is_empty()

    def count(self):
        return 0 if self.empty() else (self._right - self._left + 1)

    def clear(self):
        while not self.empty():
            self.pop_front()
        self._shadow.clear()
        self._left = 0
        self._right = -1

    def to_list(self):
        out = []
        i = self._left
        while i <= self._right:
            out.append(self._shadow.get(i, None))
            i += 1
        return out

    def __len__(self):
        return self.count()

    def __iter__(self):
        i = self._left
        while i <= self._right:
            yield self._shadow.get(i, None)
            i += 1

    def __repr__(self):
        return f"Deque(size={self.count()})"
