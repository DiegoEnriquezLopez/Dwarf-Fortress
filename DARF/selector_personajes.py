# selector_personajes.py

from Heap import QHeap
from ListaEnlazada import LinkedList, to_list, length
from deque import Deque


class SelectorPersonajes:
    def __init__(self, gestor_poblacion):
        self.gestor = gestor_poblacion
        self.umbral_vida_critica = 50
        self.umbral_vida_baja = 70

    def seleccionar_mejor_personaje(self, tipo_tarea):
        tipos_requeridos = self._obtener_tipos_para_tarea(tipo_tarea)
        heap_candidatos = QHeap()

        enanos = to_list(self.gestor.todos_enanos)
        n = length(self.gestor.todos_enanos)
        i = 0
        while i < n:
            enano = enanos[i]
            if self._es_candidato_valido(enano, tipos_requeridos):
                pr = self._calcular_prioridad(enano, tipo_tarea)
                heap_candidatos.enqueue(-pr, enano)
            i += 1

        if heap_candidatos.is_empty():
            return None

        _, mejor = heap_candidatos.dequeue()
        return mejor

    def obtener_lista_priorizada(self, tipo_tarea, max_resultados=5):
        tipos_requeridos = self._obtener_tipos_para_tarea(tipo_tarea)
        heap_candidatos = QHeap()

        enanos = to_list(self.gestor.todos_enanos)
        n = length(self.gestor.todos_enanos)
        i = 0
        while i < n:
            enano = enanos[i]
            if self._es_candidato_valido(enano, tipos_requeridos):
                pr = self._calcular_prioridad(enano, tipo_tarea)
                heap_candidatos.enqueue(-pr, enano)
            i += 1

        res = LinkedList()
        cont = 0
        while (not heap_candidatos.is_empty()) and cont < max_resultados:
            pr, pj = heap_candidatos.dequeue()
            res.add((pj, -pr, pj.salud, pj.nivel, pj.tipo))
            cont += 1
        return res

    def diagnosticar_candidatos(self, tipo_tarea):
        tipos_requeridos = self._obtener_tipos_para_tarea(tipo_tarea)
        heap_diag = QHeap()

        enanos = to_list(self.gestor.todos_enanos)
        n = length(self.gestor.todos_enanos)
        i = 0
        while i < n:
            enano = enanos[i]
            invalido = False
            razon = ""

            if not enano.esta_vivo():
                invalido = True
                razon += "Muerto; "
            if enano.salud < self.umbral_vida_critica:
                invalido = True
                razon += "Vida crítica; "
            if enano.accion_actual is not None:
                invalido = True
                razon += "Ocupado; "
            if not self._tipo_en_lista(enano.tipo, tipos_requeridos):
                invalido = True
                razon += "Tipo incorrecto; "

            if invalido:
                pr = 0
                estado = "NO"
            else:
                pr = self._calcular_prioridad(enano, tipo_tarea)
                estado = "OK"

            heap_diag.enqueue(-pr, (enano, estado, razon if razon != "" else "OK", pr))
            i += 1

        print("\n=== DIAGNÓSTICO PARA TAREA:", tipo_tarea, "===\n")
        print(f"{'Nombre':<12} {'Tipo':<12} {'Salud':>6} {'Nivel':>5} {'Energía':>7} {'Prior':>7} {'Est':<4} {'Razón'}")
        print("=" * 110)
        while not heap_diag.is_empty():
            _, data = heap_diag.dequeue()
            enano, estado, razon, pr = data
            nombre = getattr(enano, "simbolo", enano.tipo)
            print(
                f"{nombre:<12} {enano.tipo:<12} {enano.salud:>6.0f} {enano.nivel:>5} "
                f"{enano.energia:>7.0f} {pr:>7.1f} {estado:<4} {razon}"
            )

    # ========= helpers internos =========

    def _obtener_tipos_para_tarea(self, tipo_tarea):
        lista = LinkedList()
        if tipo_tarea == "minar":
            lista.add("Minero")
        elif tipo_tarea == "talar":
            lista.add("Leñador")
        elif tipo_tarea == "construir":
            lista.add("Constructor")
        elif tipo_tarea == "ordeñar":
            lista.add("Granjero")
        elif tipo_tarea == "huevos":
            lista.add("Granjero")
        elif tipo_tarea == "plantar":
            lista.add("Granjero")
        elif tipo_tarea == "cosechar":
            lista.add("Granjero")
        elif tipo_tarea == "comer":
            lista.add("Enano")
            lista.add("Minero")
            lista.add("Leñador")
            lista.add("Granjero")
            lista.add("Constructor")
        elif tipo_tarea == "defender":
            lista.add("Enano")
        return lista

    def _tipo_en_lista(self, tipo, lista_tipos):
        tipos = to_list(lista_tipos)
        n = length(lista_tipos)
        i = 0
        while i < n:
            if tipos[i] == tipo:
                return True
            i += 1
        return False

    def _es_candidato_valido(self, personaje, tipos_requeridos):
        if not personaje.esta_vivo():
            return False
        if personaje.salud < self.umbral_vida_critica:
            return False
        if personaje.accion_actual is not None:
            return False
        if not self._tipo_en_lista(personaje.tipo, tipos_requeridos):
            return False

        temp = Deque()
        encontrado = False

        while not self.gestor.enanos_disponibles.empty():
            e = self.gestor.enanos_disponibles.pop_front()
            temp.push_back(e)
            if e == personaje:
                encontrado = True

        while not temp.empty():
            self.gestor.enanos_disponibles.push_back(temp.pop_front())

        return encontrado

    def _calcular_prioridad(self, personaje, tipo_tarea):
        vida = personaje.salud
        nivel = personaje.nivel
        energia = personaje.energia

        compat = personaje.calcular_compatibilidad(tipo_tarea) * 0.5
        pr = compat

        if vida > self.umbral_vida_baja:
            pr += 1000
            pr += nivel * 100
            pr += vida * 2
            pr += energia * 0.5
        else:
            pr += 500
            pr += vida * 8
            pr += nivel * 15
            pr += energia * 0.2

        if hasattr(personaje, "clase"):
            from personajes import ClasePersonaje
            if personaje.clase == ClasePersonaje.EXPERTO:
                pr += 30
            elif personaje.clase == ClasePersonaje.INTERMEDIO:
                pr += 15

        return pr


def seleccionar_personaje_inteligente(gestor, tipo_tarea):
    sel = SelectorPersonajes(gestor)
    return sel.seleccionar_mejor_personaje(tipo_tarea)


def obtener_mejores_candidatos(gestor, tipo_tarea, cantidad=3):
    sel = SelectorPersonajes(gestor)
    return sel.obtener_lista_priorizada(tipo_tarea, cantidad)
