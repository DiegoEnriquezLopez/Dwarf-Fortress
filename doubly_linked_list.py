class DNode:
    def __init__(self, data):
        self.__data = data
        self.__next = None
        self.__prev = None
    
    def set_data(self, data):
        self.__data = data
    
    def get_data(self):
        return self.__data
    
    def set_next(self, node):
        self.__next = node
    
    def get_next(self):
        return self.__next
    
    def set_prev(self, node):
        self.__prev = node
    
    def get_prev(self):
        return self.__prev
    

class DoublyLinkedList:
    def __init__(self, data=None):
        self.__head = None
        self.__tail = None
        
        if data is not None:
            try:
                for d in data:
                    self.append(d)
            except TypeError:
                self.append(data)
        
    def append(self, data):
        new_node = DNode(data)
        if self.is_empty():
            self.__head = self.__tail = new_node
            return
        self.__tail.set_next(new_node)
        new_node.set_prev(self.__tail)
        self.__tail = new_node
    
    def preppend(self, data):  
        new_node = DNode(data)
        if self.is_empty():
            self.__head = self.__tail = new_node
            return
        self.__head.set_prev(new_node)
        new_node.set_next(self.__head)
        self.__head = new_node
    
    def __remove_index(self, index):
        if self.is_empty():
            raise Exception("removing from empty list")
        if index < 0 or not isinstance(index, int):
            raise IndexError("index must be positive _int_")
        
        current = self.__head
        idx = 0
        
        while current is not None:
            if idx == index:
                if current == self.__head:
                    self.__head = current.get_next()
                    if self.__head is not None:
                        self.__head.set_prev(None)
                    else:
                        self.__tail = None
                elif current == self.__tail:
                    self.__tail = current.get_prev()
                    if self.__tail is not None:
                        self.__tail.set_next(None)
                    else:
                        self.__head = None
                else:
                    prev = current.get_prev()
                    nxt = current.get_next()
                    prev.set_next(nxt)
                    nxt.set_prev(prev)
                return
            current = current.get_next()
            idx += 1
        raise IndexError("index out of range")

    def __remove_value(self, value):
        if self.is_empty():
            raise Exception("removing from empty list")
        current = self.__head
        while current is not None:
            if current.get_data() == value:
                if current == self.__head:
                    self.__head = current.get_next()
                    if self.__head is not None:
                        self.__head.set_prev(None)
                    else:
                        self.__tail = None
                elif current == self.__tail:
                    self.__tail = current.get_prev()
                    if self.__tail is not None:
                        self.__tail.set_next(None)
                    else:
                        self.__head = None
                else:
                    current.get_prev().set_next(current.get_next())
                    current.get_next().set_prev(current.get_prev())
                return  # salir tras borrar una coincidencia
            current = current.get_next()

    def remove(self, index=None, value=None):
        if self.is_empty():
            raise Exception("removing from empty list")
        if index is not None and value is not None:
            raise Exception("index and value must be given exclusively")
        if index is not None:
            self.__remove_index(index)
        if value is not None:
            self.__remove_value(value)
        
    def is_empty(self):
        return self.__head is None

    def find(self, predicate):
        resultados = []
        cur = self.__head
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
        cur = self.__head
        while cur is not None:
            out.append(cur.get_data())
            cur = cur.get_next()
        return out

    def __len__(self):
        n = 0
        cur = self.__head
        while cur is not None:
            n += 1
            cur = cur.get_next()
        return n

    def __iter__(self):
        cur = self.__head
        while cur is not None:
            yield cur.get_data()
            cur = cur.get_next()
