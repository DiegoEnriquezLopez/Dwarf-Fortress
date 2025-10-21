import random 

class Nodo:
    """Nodo para lista enlazada"""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
        self.anterior = None


class ListaEnlazada:
    """Lista doblemente enlazada"""
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamanio = 0
    
    def esta_vacia(self):
        return self.cabeza is None
    
    def agregar_al_final(self, dato):
        """Agrega un elemento al final de la lista"""
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            self.cola.siguiente = nuevo
            nuevo.anterior = self.cola
            self.cola = nuevo
        self.tamanio += 1
    
    def agregar_al_inicio(self, dato):
        """Agrega un elemento al inicio de la lista"""
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.cabeza = self.cola = nuevo
        else:
            nuevo.siguiente = self.cabeza
            self.cabeza.anterior = nuevo
            self.cabeza = nuevo
        self.tamanio += 1
    
    def eliminar(self, dato):
        """Elimina un elemento específico de la lista"""
        actual = self.cabeza
        while actual:
            if actual.dato == dato:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.cola = actual.anterior
                
                self.tamanio -= 1
                return True
            actual = actual.siguiente
        return False
    
    def buscar(self, criterio):
        """Busca elementos que cumplan un criterio (función lambda)"""
        resultados = []
        actual = self.cabeza
        while actual:
            if criterio(actual.dato):
                resultados.append(actual.dato)
            actual = actual.siguiente
        return resultados
    
    def obtener_lista(self):
        """Retorna todos los elementos como lista de Python (para debug)"""
        elementos = []
        actual = self.cabeza
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos
    
    def __len__(self):
        return self.tamanio
    
    def __iter__(self):
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente


class Deque:
    """Deque (cola de doble extremo) para gestión de disponibilidad"""
    def __init__(self):
        self.items = ListaEnlazada()
    
    def esta_vacia(self):
        return self.items.esta_vacia()
    
    def agregar_frente(self, item):
        """Agrega al frente (mayor prioridad)"""
        self.items.agregar_al_inicio(item)
    
    def agregar_atras(self, item):
        """Agrega al final (menor prioridad)"""
        self.items.agregar_al_final(item)
    
    def quitar_frente(self):
        """Quita del frente"""
        if self.esta_vacia():
            raise IndexError("Deque vacío")
        dato = self.items.cabeza.dato
        self.items.eliminar(dato)
        return dato
    
    def quitar_atras(self):
        """Quita del final"""
        if self.esta_vacia():
            raise IndexError("Deque vacío")
        dato = self.items.cola.dato
        self.items.eliminar(dato)
        return dato
    
    def ver_frente(self):
        """Ver elemento del frente sin quitarlo"""
        if self.esta_vacia():
            return None
        return self.items.cabeza.dato
    
    def ver_atras(self):
        """Ver elemento del final sin quitarlo"""
        if self.esta_vacia():
            return None
        return self.items.cola.dato
    
    def tamanio(self):
        return len(self.items)
    
    def obtener_lista(self):
        return self.items.obtener_lista()
    
    def __len__(self):
        return len(self.items)
    
    def __iter__(self):
        return iter(self.items)
