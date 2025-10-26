class DNode:
    def __init__(self, data):
        self._data = data
        self._next = None
        self._prev = None
    
    def set_data(self, data):
        self._data = data
    
    def get_data(self):
        return self._data
    
    def set_next(self, node):
        self._next = node
    
    def get_next(self):
        return self._next
    
    def set_prev(self, node):
        self._prev = node
    
    def get_prev(self):
        return self._prev
        

class DoublyLinkedList:
    def __init__(self, data=None):
        self._head = None
        self._tail = None
        
        if data is not None:
            try:
                for d in data:
                    self.append(d)
            except TypeError:
                self.append(data)
        
    def append(self, data):
        new_node = DNode(data)
        if self.is_empty():
            self._head = self._tail = new_node
            return
        
        self._tail.set_next(new_node)
        new_node.set_prev(self._tail)
        self._tail = new_node
    
    def preppend(self, data):  
        new_node = DNode(data)
        if self.is_empty():
            self._head = self._tail = new_node
            return
        
        self._head.set_prev(new_node)
        new_node.set_next(self._head)
        self._head = new_node
    
    def _remove_index(self, index):
        if self.is_empty():
            raise Exception("removing from empty list")
        if index < 0 or not isinstance(index, int):
            raise IndexError("index must be positive int")
        
        current = self._head
        idx = 0
        
        while current is not None:
            if idx == index:
                if current == self._head:
                    self._head = current.get_next()
                    if self._head is not None:
                        self._head.set_prev(None)
                    else:
                        self._tail = None
                elif current == self._tail:
                    self._tail = current.get_prev()
                    if self._tail is not None:
                        self._tail.set_next(None)
                    else:
                        self._head = None
                else:
                    prev = current.get_prev()
                    nxt = current.get_next()
                    prev.set_next(nxt)
                    nxt.set_prev(prev)
                return
            current = current.get_next()
            idx += 1
        raise IndexError("index out of range")

    def _remove_value(self, value):
        if self.is_empty():
            raise Exception("removing from empty list")
        current = self._head
        while current is not None:
            if current.get_data() == value:
                if current == self._head:
                    self._head = current.get_next()
                    if self._head is not None:
                        self._head.set_prev(None)
                    else:
                        self._tail = None
                elif current == self._tail:
                    self._tail = current.get_prev()
                    if self._tail is not None:
                        self._tail.set_next(None)
                    else:
                        self._head = None
                else:
                    current.get_prev().set_next(current.get_next())
                    current.get_next().set_prev(current.get_prev())
                return  
            current = current.get_next()

    def remove(self, index=None, value=None):
        if self.is_empty():
            raise Exception("removing from empty list")
        if index is not None and value is not None:
            raise Exception("index and value must be given exclusively")
        if index is not None:
            self._remove_index(index)
        if value is not None:
            self._remove_value(value)
        
    def is_empty(self):
        return self._head is None

    def find(self, predicate):
        resultados = []
        cur = self._head
        while cur is not None:
            d = cur.get_data()
            try:
                if predicate(d):
                    resultados.append(d)
            except Exception:
                pass
            cur = cur.get_next()
        return resultados

    def to_list(self):
        out = []
        cur = self._head
        while cur is not None:
            out.append(cur.get_data())
            cur = cur.get_next()
        return out

    def __len__(self):
        n = 0
        cur = self._head
        while cur is not None:
            n += 1
            cur = cur.get_next()
        return n

    def __iter__(self):
        cur = self._head
        while cur is not None:
            yield cur.get_data()
            cur = cur.get_next()
