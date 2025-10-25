class Node:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.parent = None
        self.left = None
        self.right = None

class QHeap:
    def __init__(self, data=None):
        self.__root = None
        self.__size = 0
        if data:
            try:
                for k, d in data:
                    self.enqueue(k, d)
            except Exception:
                self.enqueue(data[0], data[1])

    def enqueue(self, key, data):
        new_node = Node(key, data)
        if self.is_empty():
            self.__root = new_node
        else:
            self.__insert_node(new_node)
            self.__bubble_up(new_node)
        self.__size += 1

    def dequeue(self):
        if self.is_empty():
            raise Exception("dequeue from empty queue")
        key, data = self.__root.key, self.__root.data
        if not self.__root.left:
            self.__root = None
        else:
            last = self.__get_last_node()
            self.__swap(self.__root, last)
            self.__remove_last_node()
            self.__bubble_down(self.__root)
        self.__size -= 1
        return key, data

    def is_empty(self):
        return self.__root is None

    def __insert_node(self, node):
        path = bin(self.__size + 1)[3:]
        current = self.__root
        parent = None
        for b in path:
            parent = current
            current = current.left if b == '0' else current.right
        if not parent.left:
            parent.left = node
            node.parent = parent
        else:
            parent.right = node
            node.parent = parent

    def __swap(self, n1, n2):
        self.__swap_node_values(n1, n2)

    def __swap_node_values(self, n1, n2):
        n1.key, n2.key = n2.key, n1.key
        n1.data, n2.data = n2.data, n1.data

    def __bubble_up(self, node):
        while node.parent:
            if node.parent.key > node.key:
                self.__swap_node_values(node, node.parent)
                node = node.parent
            else:
                break

    def __get_last_node(self):
        path = bin(self.__size)[3:]
        current = self.__root
        for b in path:
            current = current.left if b == '0' else current.right
        return current

    def __remove_last_node(self):
        path = bin(self.__size)[3:]
        parent = self.__root
        current = self.__root
        last_bit = None
        if not path:
            self.__root = None
            return
        for b in path:
            last_bit = b
            parent = current
            current = current.left if b == '0' else current.right
        if last_bit == '0':
            parent.left = None
        else:
            parent.right = None

    def __bubble_down(self, node):
        while node and node.left:
            child = node.left
            if node.right and node.right.key < node.left.key:
                child = node.right
            if node.key > child.key:
                self.__swap_node_values(node, child)
                node = child
            else:
                break

def merge(heap1, heap2):
    temp = QHeap()
    while not heap2.is_empty():
        k, d = heap2.dequeue()
        temp.enqueue(k, d)
        heap1.enqueue(k, d)
    while not temp.is_empty():
        k, d = temp.dequeue()
        heap2.enqueue(k, d)

def merge_recursive(heap1, heap2):
    if heap2.is_empty():
        return
    k, d = heap2.dequeue()
    merge_recursive(heap1, heap2)
    heap2.enqueue(k, d)
    heap1.enqueue(k, d)

def change_priority(heap, old_key, new_key):
    temp = QHeap()
    while not heap.is_empty():
        k, d = heap.dequeue()
        if k == old_key:
            temp.enqueue(new_key, d)
        else:
            temp.enqueue(k, d)
    while not temp.is_empty():
        k, d = temp.dequeue()
        heap.enqueue(k, d)

def rearrange(heap, temp):
    while not temp.is_empty():
        k, d = temp.dequeue()
        heap.enqueue(k, d)

def remove(heap, old_key):
    temp = QHeap()
    while not heap.is_empty():
        k, d = heap.dequeue()
        if k != old_key:
            temp.enqueue(k, d)
    rearrange(heap, temp)

def convert_to_min_heap(max_heap):
    min_heap = QHeap()
    while not max_heap.is_empty():
        k, d = max_heap.dequeue()
        min_heap.enqueue(-k, d)
    return min_heap

def toss(heap):
    temp = QHeap()
    while not heap.is_empty():
        k, d = heap.dequeue()
        n = Node(k, d)
        if temp.is_empty():
            temp._QHeap__root = n
            temp._QHeap__size = 1
        else:
            temp._QHeap__insert_node(n)
            temp._QHeap__size += 1
    for k, d in [(3, 7), (5, 2), (2, 8), (1, 5)]:
        n = Node(k, d)
        if temp.is_empty():
            temp._QHeap__root = n
            temp._QHeap__size = 1
        else:
            temp._QHeap__insert_node(n)
            temp._QHeap__size += 1
    rearrange(heap, temp)

def print_top_k(k):
    if k.is_empty():
        return
    heap1 = QHeap()
    heap2 = QHeap()
    count = 0
    limite = 3
    negative = False
    positive = False
    while not k.is_empty():
        key, data = k.dequeue()
        if key < 0:
            negative = True
        if key > 0:
            positive = True
        heap1.enqueue(key, data)
        heap2.enqueue(key, data)
    while not heap1.is_empty():
        key, data = heap1.dequeue()
        k.enqueue(key, data)
    negation = False
    if negative:
        if not positive:
            negation = True
    while not heap2.is_empty():
        if count >= limite:
            break
        key, data = heap2.dequeue()
        if negation:
            priority = -key
        else:
            priority = key
        print(priority, data)
        count += 1

def is_valid_heap(node, is_max_heap=True):
    if not node:
        return True
    if node.left:
        if is_max_heap and node.priority < node.left.priority:
            return False
        if not is_max_heap and node.priority > node.left.priority:
            return False
    if node.rigth:
        if is_max_heap and node.priority < node.rigth.priority:
            return False
        if not is_max_heap and node.priority > node.rigth.priority:
            return False
    return is_valid_heap(node.left, is_max_heap) and is_valid_heap(node.rigth, is_max_heap)

def merge_multiple_heaps(heaps):
    temp1 = QHeap()
    temp2 = QHeap()
    for h in heaps:
        while not h.is_empty():
            k, d = h.dequeue()
            temp1.enqueue(k, d)
            temp2.enqueue(k, d)
        while not temp1.is_empty():
            k, d = temp1.dequeue()
            h.enqueue(k, d)
    return temp2
