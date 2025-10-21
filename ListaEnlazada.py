class Node:
    def __init__(self, data):
        self._data = data
        self._next = None
        
    def set_data(self, data):
        self._data = data 
        
    def get_data(self):
        return self._data 
    
    def set_next(self, node):
        self._next = node 
        
    def get_next(self):
        return self._next   


class LinkedList:
    def __init__(self):
        self.__head = None

    def add(self, data):
        new_node = Node(data)
        if not self.__head:
            self.__head = new_node
            return
        current = self.__head
        while current.get_next() is not None:
            current = current.get_next()
        current.set_next(new_node)

    def insert_init(self, data):
        new_node = Node(data)
        new_node.set_next(self.__head)
        self.__head = new_node

    def remove_index(self, index):
        if self.is_empty():
            raise Exception("removing from empty list")
        if index < 0:
            raise Exception("index out of range")

        current = self.__head
        prev = None
        idx = 0
        while current:
            if idx == index:
                if prev is None:
                    self.__head = current.get_next()
                else:
                    prev.set_next(current.get_next())
                return
            prev = current
            current = current.get_next()
            idx += 1
        raise Exception("index out of range")

    def remove_value(self, value):
        if self.is_empty():
            return False
        prev = None
        current = self.__head
        while current is not None:
            if current.get_data() == value:
                nxt = current.get_next()
                if prev is None:
                    self.__head = nxt
                else:
                    prev.set_next(nxt)
                return True
            prev = current
            current = current.get_next()
        return False

    def find(self, predicate):
        results = []
        current = self.__head
        while current is not None:
            d = current.get_data()
            try:
                if predicate(d):
                    results.append(d)
            except Exception:
                pass
            current = current.get_next()
        return results

    def to_list(self):
        out = []
        current = self.__head
        while current is not None:
            out.append(current.get_data())
            current = current.get_next()
        return out

    def is_empty(self):
        return self.__head is None

    def __len__(self):
        n = 0
        current = self.__head
        while current is not None:
            n += 1
            current = current.get_next()
        return n

    def __iter__(self):
        current = self.__head
        while current is not None:
            yield current.get_data()
            current = current.get_next()

