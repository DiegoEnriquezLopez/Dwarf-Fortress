# gestion.py 

from ListaEnlazada import LinkedList, to_list, length
from deque import Deque


class GestorPoblacion:

    def __init__(self):
        self.enanos_disponibles = Deque()
        self.enanos_ocupados = LinkedList()
        self.enanos_descansando = LinkedList()
        self.todos_enanos = LinkedList()

    # ---------------- altas ----------------
    def agregar_enano(self, enano):
        self.enanos_disponibles.push_back(enano)
        self.todos_enanos.add(enano)

    # ---------------- asignación ----------------
    def obtener_enano_disponible(self):
        if self.enanos_disponibles.empty():
            return None
        return self.enanos_disponibles.pop_front()

    def marcar_ocupado(self, enano, accion):
        enano.asignar_accion(accion)
        self.enanos_ocupados.add(enano)
        # lo quitamos de disponibles si estaba ahí
        tmp = []
        while not self.enanos_disponibles.empty():
            e = self.enanos_disponibles.pop_front()
            if e != enano:
                tmp.append(e)
        for e in tmp:
            self.enanos_disponibles.push_back(e)

    def liberar_enano(self, enano):
        resultado = enano.completar_accion()
        self.enanos_ocupados.remove_value(enano)
        if enano.energia < 30:
            self.enanos_descansando.add(enano)
        else:
            self.enanos_disponibles.push_back(enano)
        return resultado

    def obtener_enanos_disponibles(self):
        # cuenta sin usar len()
        cont = 0
        tmp = []
        while not self.enanos_disponibles.empty():
            e = self.enanos_disponibles.pop_front()
            tmp.append(e)
            cont += 1
        for e in tmp:
            self.enanos_disponibles.push_back(e)
        return cont

    # ---------------- ciclo de actualización ----------------
    def actualizar_poblacion(self):
        # bajar tiempo a ocupados
        for enano in to_list(self.enanos_ocupados):
            enano.tiempo_ocupado -= 1
            if enano.tiempo_ocupado <= 0:
                self.liberar_enano(enano)

        # recuperar a los que descansan
        for enano in to_list(self.enanos_descansando):
            enano.descansar()
            if enano.energia >= 90:
                self.enanos_descansando.remove_value(enano)
                self.enanos_disponibles.push_back(enano)

    # ---------------- stats ----------------
    def obtener_estadisticas(self):
        # contar disponibles
        disp = 0
        tmp = []
        while not self.enanos_disponibles.empty():
            e = self.enanos_disponibles.pop_front()
            tmp.append(e)
            disp += 1
        for e in tmp:
            self.enanos_disponibles.push_back(e)

        vivos = 0
        muertos = 0
        for e in to_list(self.todos_enanos):
            if e.esta_vivo():
                vivos += 1
            else:
                muertos += 1

        return {
            'total_enanos': length(self.todos_enanos),
            'disponibles': disp,
            'ocupados': length(self.enanos_ocupados),
            'descansando': length(self.enanos_descansando),
            'vivos': vivos,
            'muertos': muertos,
        }

    def mostrar_estado(self):
        return self.obtener_estadisticas()

    def limpiar_muertos(self):
        # quita muertos de todos los contenedores
        for e in to_list(self.todos_enanos):
            if not e.esta_vivo():
                self.enanos_ocupados.remove_value(e)
                self.enanos_descansando.remove_value(e)
        tmp = []
        while not self.enanos_disponibles.empty():
            e = self.enanos_disponibles.pop_front()
            if e.esta_vivo():
                tmp.append(e)
        for e in tmp:
            self.enanos_disponibles.push_back(e)
