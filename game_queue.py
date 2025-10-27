class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__(self, acciones=None):
        self.front = None
        self.rear = None
        self.size = 0
        if acciones is not None:
            try:
                for a in acciones:
                    self.enqueue(a)
            except TypeError:
                self.enqueue(acciones)

    def enqueue(self, a):
        node = Node(a)
        if self.front is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        if self.front is None:
            raise Exception("empty")
        val = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self.size -= 1
        return val
    
    def empty(self):
        return self.front is None
    
    def peek(self):
        return None if self.front is None else self.front.data

def count(queue):
    return queue.size


def clear(queue):
    queue.front = None
    queue.rear = None
    queue.size = 0

def queue_extend(q, iterable):
    if iterable is None:
        return 0

    if isinstance(iterable, str):
        q.enqueue(iterable)
        return 1

    try:
        c = 0
        for a in iterable:
            q.enqueue(a)
            c += 1
        return c
    except Exception:
        q.enqueue(iterable)
        return 1
