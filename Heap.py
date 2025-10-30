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
