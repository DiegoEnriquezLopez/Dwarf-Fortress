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
        self._head = None

    def add(self, data):
        new_node = Node(data)
        if not self._head:
            self._head = new_node
            return
        current = self._head
        while current.get_next() is not None:
            current = current.get_next()
        current.set_next(new_node)

    def insert_init(self, data):
        new_node = Node(data)
        new_node.set_next(self._head)
        self._head = new_node

    def remove_index(self, index):
        if self.is_empty():
            raise Exception("removing from empty list")
        if index < 0:
            raise Exception("index out of range")

        current = self._head
        prev = None
        idx = 0
        while current:
            if idx == index:
                if prev is None:
                    self._head = current.get_next()
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
        current = self._head
        while current is not None:
            if current.get_data() == value:
                nxt = current.get_next()
                if prev is None:
                    self._head = nxt
                else:
                    prev.set_next(nxt)
                return True
            prev = current
            current = current.get_next()
        return False
    
    def is_empty(self):
        return self._head is None

def find(lista, predicate):
    resultados = []
    current = lista._head
    while current is not None:
        d = current.get_data()
        try:
            if predicate(d):
                resultados.append(d)
        except Exception:
            pass
        current = current.get_next()
    return resultados


def to_list(lista):
    datos = []
    current = lista._head
    while current is not None:
        datos.append(current.get_data())
        current = current.get_next()
    return datos


def length(lista):
    contador = 0
    current = lista._head
    while current is not None:
        contador += 1
        current = current.get_next()
    return contador


def iterate(lista):
    current = lista._head
    while current is not None:
        yield current.get_data()
        current = current.get_next()
