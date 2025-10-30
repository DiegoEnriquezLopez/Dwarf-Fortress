from ListaEnlazada import LinkedList, to_list, length
from deque import Deque


class GestorPoblacion:
    def __init__(self):
        self.enanos_disponibles = Deque()
        self.enanos_ocupados = LinkedList()
        self.enanos_descansando = LinkedList()
        self.visitantes = LinkedList()
        self.enemigos = LinkedList()
        self.todos_enanos = LinkedList()

    def agregar_enano(self, enano):
        self.todos_enanos.add(enano)
        if enano.esta_disponible():
            self.enanos_disponibles.push_back(enano)

    def obtener_enano_disponible(self):
        if not self.enanos_disponibles.empty():
            return self.enanos_disponibles.pop_front()
        return None

    def obtener_mejor_enano_para(self, tipo_accion):
        if self.enanos_disponibles.empty():
            return None
        mejor_enano = None
        mejor_compatibilidad = -1
        temp = []
        while not self.enanos_disponibles.empty():
            enano = self.enanos_disponibles.pop_front()
            compatibilidad = enano.calcular_compatibilidad(tipo_accion)
            if compatibilidad > mejor_compatibilidad and enano.energia > 20:
                if mejor_enano:
                    temp.append(mejor_enano)
                mejor_enano = enano
                mejor_compatibilidad = compatibilidad
            else:
                temp.append(enano)
        for enano in temp:
            self.enanos_disponibles.push_back(enano)
        return mejor_enano

    def marcar_ocupado(self, enano, accion):
        enano.asignar_accion(accion)
        self.enanos_ocupados.add(enano)
        temp = []
        while not self.enanos_disponibles.empty():
            e = self.enanos_disponibles.pop_front()
            if e != enano:
                temp.append(e)
        for e in temp:
            self.enanos_disponibles.push_back(e)

    def liberar_enano(self, enano):
        resultado = enano.completar_accion()
        self.enanos_ocupados.remove_value(enano)
        if enano.energia < 30:
            self.enanos_descansando.add(enano)
        else:
            self.enanos_disponibles.push_back(enano)
        return resultado

    def actualizar_poblacion(self):
        ocupados_temp = to_list(self.enanos_ocupados)
        for enano in ocupados_temp:
            enano.tiempo_ocupado -= 1
            if enano.tiempo_ocupado <= 0:
                self.liberar_enano(enano)
        descansando_temp = to_list(self.enanos_descansando)
        for enano in descansando_temp:
            enano.descansar()
            if enano.energia >= 70:
                self.enanos_descansando.remove_value(enano)
                self.enanos_disponibles.push_back(enano)
        todos_temp = to_list(self.todos_enanos)
        for enano in todos_temp:
            enano.actualizar_necesidades()

    def agregar_visitante(self, personaje):
        self.visitantes.add(personaje)

    def agregar_enemigo(self, enemigo):
        self.enemigos.add(enemigo)

    def remover_enemigo(self, enemigo):
        self.enemigos.remove_value(enemigo)

    def obtener_enemigos_activos(self):
        enemigos = to_list(self.enemigos)
        return [e for e in enemigos if e.salud > 0]

    def obtener_enanos_disponibles(self):
        temp = []
        disponibles = []
        while not self.enanos_disponibles.empty():
            enano = self.enanos_disponibles.pop_front()
            if enano.esta_disponible():
                disponibles.append(enano)
            temp.append(enano)
        for enano in temp:
            self.enanos_disponibles.push_back(enano)
        return disponibles

    def obtener_estadisticas(self):
        disponibles_count = 0
        temp = []
        while not self.enanos_disponibles.empty():
            temp.append(self.enanos_disponibles.pop_front())
            disponibles_count += 1
        for e in temp:
            self.enanos_disponibles.push_back(e)
        return {
            'total_enanos': length(self.todos_enanos),
            'disponibles': disponibles_count,
            'ocupados': length(self.enanos_ocupados),
            'descansando': length(self.enanos_descansando),
            'visitantes': length(self.visitantes),
            'enemigos': length(self.enemigos),
            'vivos': sum(1 for e in to_list(self.todos_enanos) if e.esta_vivo()),
            'muertos': sum(1 for e in to_list(self.todos_enanos) if not e.esta_vivo())
        }

    def mostrar_estado(self):
        return self.obtener_estadisticas()

    def limpiar_muertos(self):
        todos_temp = to_list(self.todos_enanos)
        for enano in todos_temp:
            if not enano.esta_vivo():
                self.enanos_ocupados.remove_value(enano)
                self.enanos_descansando.remove_value(enano)
        temp = []
        while not self.enanos_disponibles.empty():
            enano = self.enanos_disponibles.pop_front()
            if enano.esta_vivo():
                temp.append(enano)
        for enano in temp:
            self.enanos_disponibles.push_back(enano)
