# planificador.py

from game_queue import Queue, count
from Heap import QHeap
from enum import Enum


class TipoEvento(Enum):
    ORDEN_USUARIO = "orden_usuario"
    ATAQUE_ENEMIGO = "ataque_enemigo"
    HAMBRE_CRITICA = "hambre_critica"


class PlanificadorTareas:
    def __init__(self, estado_juego):
        self.estado_juego = estado_juego
        self.buffer_ordenes = Queue()
        self.heap_prioridades = QHeap()
        self.acciones_ejecutadas = []
        self._tamanio_heap = 0

    def registrar_evento(self, evento_tipo, detalles=None):
        if detalles is None:
            detalles = {}
        if evento_tipo == TipoEvento.ORDEN_USUARIO:
            accion = detalles.get('accion')
            self._encolar_orden_usuario(accion, detalles.get('parametros', {}))
        elif evento_tipo == TipoEvento.ATAQUE_ENEMIGO:
            enemigo = detalles.get('enemigo')
            self._generar_orden_defender(enemigo)
        elif evento_tipo == TipoEvento.HAMBRE_CRITICA:
            self._generar_orden_comer()

    def _encolar_orden_usuario(self, accion, parametros):
        if accion is None:
            return
        orden = {
            'tipo_evento': TipoEvento.ORDEN_USUARIO,
            'accion': accion,
            'parametros': parametros,
            'timestamp': getattr(self.estado_juego, 'tiempo_actual', 0)
        }
        self.buffer_ordenes.enqueue(orden)

    def _generar_orden_defender(self, enemigo):
        orden = {
            'tipo_evento': TipoEvento.ATAQUE_ENEMIGO,
            'accion': 'defender',
            'parametros': {'enemigo': enemigo},
            'timestamp': getattr(self.estado_juego, 'tiempo_actual', 0)
        }
        self.buffer_ordenes.enqueue(orden)

    def _generar_orden_comer(self):
        orden = {
            'tipo_evento': TipoEvento.HAMBRE_CRITICA,
            'accion': 'comer',
            'parametros': {},
            'timestamp': getattr(self.estado_juego, 'tiempo_actual', 0)
        }
        self.buffer_ordenes.enqueue(orden)

    def procesar_buffer(self):
        while not self.buffer_ordenes.empty():
            orden = self.buffer_ordenes.dequeue()
            prioridad = self._calcular_prioridad(orden)
            self.heap_prioridades.enqueue(prioridad, orden)
            self._tamanio_heap += 1

    def _calcular_prioridad(self, orden):
        tipo = orden['tipo_evento']
        accion = orden['accion']
        urg_evt = self._calcular_urgencia_evento(tipo)
        urg_rec = self._calcular_urgencia_recursos(accion)
        disponibilidad = 1.0
        if hasattr(self.estado_juego, 'gestor'):
            libres = self.estado_juego.gestor.obtener_enanos_disponibles()
            if libres > 0:
                disponibilidad = 1.0 + (libres / 5.0)
        prioridad = int(urg_evt * 10 + urg_rec * 5 + disponibilidad * 3)
        if prioridad < 1:
            prioridad = 1
        return prioridad

    def _calcular_urgencia_evento(self, tipo_evento):
        if tipo_evento == TipoEvento.ATAQUE_ENEMIGO:
            return 5.0
        if tipo_evento == TipoEvento.HAMBRE_CRITICA:
            return 4.0
        return 2.0

    def _calcular_urgencia_recursos(self, accion):
        if not hasattr(self.estado_juego, 'recursos'):
            return 0.0
        r = self.estado_juego.recursos
        urg = 0.0
        if accion == 'talar' and r.get('madera', 0) < 10:
            urg += 2.5
        if accion == 'minar' and r.get('piedra', 0) < 10:
            urg += 2.5
        if accion in ('plantar', 'cosechar', 'ordeñar', 'huevos') and r.get('comida', 0) < 15:
            urg += 2.0
        return urg

    def obtener_siguiente_tarea(self):
        if self._tamanio_heap == 0:
            return None
        prioridad, tarea = self.heap_prioridades.dequeue()
        self._tamanio_heap -= 1
        tarea['duracion'] = self._calcular_duracion(tarea['accion'])
        return tarea

    def _calcular_duracion(self, accion):
        duraciones = {
            'minar': 60,
            'talar': 45,
            'construir': 30,
            'plantar': 15,
            'cosechar': 20,
            'ordeñar': 30,
            'huevos': 30,
            'comer': 8,
            'defender': 20,
        }
        return duraciones.get(accion, 10)

    def obtener_estadisticas(self):
        buffer_count = count(self.buffer_ordenes)
        return {
            'ordenes_en_buffer': buffer_count,
            'tareas_en_heap': self._tamanio_heap,
            'acciones_completadas': len(self.acciones_ejecutadas)
        }

    def mostrar_estado(self):
        return self.obtener_estadisticas()
