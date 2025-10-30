from game_queue import Queue, count
from Heap import QHeap, change_priority
from enum import Enum


class TipoEvento(Enum):
    ORDEN_USUARIO = "orden_usuario"
    CLIMA_TORMENTA = "clima_tormenta"
    CLIMA_TORNADO = "clima_tornado"
    CLIMA_LLUVIA = "clima_lluvia"
    ATAQUE_ENEMIGO = "ataque_enemigo"
    HAMBRE_CRITICA = "hambre_critica"
    EDIFICIO_DAÑADO = "edificio_dañado"


class Planificador:
    def __init__(self, gestor_poblacion, estado_juego, bar=None):
        self.buffer_ordenes = Queue()
        self.cola_prioridades = QHeap()
        self.gestor = gestor_poblacion
        self.estado_juego = estado_juego
        self.bar = bar  # <-- NUEVO
        self.acciones_ejecutadas = []
        self._tamanio_heap = 0

    def agregar_orden_usuario(self, accion_tipo, parametros=None):
        orden = {
            'tipo_evento': TipoEvento.ORDEN_USUARIO,
            'accion': accion_tipo,
            'parametros': parametros or {},
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        }
        self.buffer_ordenes.enqueue(orden)
        print(f"📥 Orden agregada al buffer: {accion_tipo}")

    def generar_ordenes_por_evento(self, evento_tipo, detalles=None):
        detalles = detalles or {}

        if evento_tipo == TipoEvento.CLIMA_TORMENTA:
            self._generar_orden_resguardo()
            print("⛈️ Tormenta - Orden de resguardo generada")

        elif evento_tipo == TipoEvento.CLIMA_TORNADO:
            self._generar_orden_resguardo_urgente()
            self._generar_orden_reparar()
            print("🌪️ Tornado - Órdenes de emergencia generadas")
            self.ajustar_prioridades_por_evento(factor=0.7)

        elif evento_tipo == TipoEvento.ATAQUE_ENEMIGO:
            enemigo = detalles.get('enemigo')
            self._generar_orden_defender(enemigo)
            print(f"⚔️ Ataque enemigo - Orden de defensa generada")
            self.ajustar_prioridades_por_evento(factor=0.6)

        elif evento_tipo == TipoEvento.HAMBRE_CRITICA:
            self._generar_orden_conseguir_comida()
            print("🍖 Hambre crítica - Orden de comida generada")
            self.ajustar_prioridades_por_evento(factor=0.8)

        elif evento_tipo == TipoEvento.EDIFICIO_DAÑADO:
            edificio = detalles.get('edificio')
            self._generar_orden_reparar(edificio)
            print("🏚️ Edificio dañado - Orden de reparación generada")

    def _generar_orden_resguardo(self):
        orden = {
            'tipo_evento': TipoEvento.CLIMA_TORMENTA,
            'accion': 'resguardar',
            'parametros': {'urgencia': 'media'},
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        }
        self.buffer_ordenes.enqueue(orden)

    def _generar_orden_resguardo_urgente(self):
        orden = {
            'tipo_evento': TipoEvento.CLIMA_TORNADO,
            'accion': 'resguardar',
            'parametros': {'urgencia': 'alta'},
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        }
        self.buffer_ordenes.enqueue(orden)

    def _generar_orden_reparar(self, edificio=None):
        orden = {
            'tipo_evento': TipoEvento.EDIFICIO_DAÑADO,
            'accion': 'reparar',
            'parametros': {'edificio': edificio},
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        }
        self.buffer_ordenes.enqueue(orden)

    def _generar_orden_defender(self, enemigo):
        orden = {
            'tipo_evento': TipoEvento.ATAQUE_ENEMIGO,
            'accion': 'defender',
            'parametros': {'enemigo': enemigo},
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        }
        self.buffer_ordenes.enqueue(orden)

    def _generar_orden_conseguir_comida(self):
        orden = {
            'tipo_evento': TipoEvento.HAMBRE_CRITICA,
            'accion': 'cultivar',
            'parametros': {'urgencia': 'alta'},
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        }
        self.buffer_ordenes.enqueue(orden)

    def calcular_prioridad(self, orden, personaje):
        compatibilidad = personaje.calcular_compatibilidad(orden['accion'])
        nivel_bonus = personaje.nivel if hasattr(personaje, 'nivel') else 1

        energia_factor = personaje.energia / 100 if hasattr(personaje, 'energia') else 1.0
        salud_factor = personaje.salud / 100
        disponibilidad = (energia_factor + salud_factor) / 2

        urgencia_base = self._calcular_urgencia_evento(orden['tipo_evento'])
        urgencia_recursos = self._calcular_urgencia_recursos(orden['accion'])

        prioridad = 100 - (
            compatibilidad * 3.0 +
            nivel_bonus * 5.0 +
            disponibilidad * 10.0 +
            urgencia_base +
            urgencia_recursos
        )

        return max(1, prioridad)

    def _calcular_urgencia_evento(self, tipo_evento):
        urgencias = {
            TipoEvento.CLIMA_TORNADO: 30.0,
            TipoEvento.ATAQUE_ENEMIGO: 25.0,
            TipoEvento.HAMBRE_CRITICA: 20.0,
            TipoEvento.CLIMA_TORMENTA: 15.0,
            TipoEvento.EDIFICIO_DAÑADO: 10.0,
            TipoEvento.ORDEN_USUARIO: 5.0
        }
        return urgencias.get(tipo_evento, 5.0)

    def _calcular_urgencia_recursos(self, accion):
        urgencia = 0.0
        if hasattr(self.estado_juego, 'recursos'):
            recursos = self.estado_juego.recursos
            if accion == 'talar' and recursos.get('madera', 0) < 10:
                urgencia += 15.0
            if accion == 'minar' and recursos.get('piedra', 0) < 10:
                urgencia += 15.0
            if accion in ['cultivar', 'dar_comida_animales', 'comer']:
                comida_total = recursos.get('carne', 0) + recursos.get('trigo', 0)
                if comida_total < 20:
                    urgencia += 20.0
            if accion == 'beber':
                # ahora beber depende del BAR, pero aún puede haber urgencia
                agua = recursos.get('agua', 0)
                if agua < 5:
                    urgencia += 10.0
        return urgencia

    def procesar_ciclo(self):
        ordenes_procesadas = 0
        max_ordenes = 5

        while ordenes_procesadas < max_ordenes:
            if self.buffer_ordenes.empty():
                break

            orden = self.buffer_ordenes.dequeue()
            personajes_disponibles = self._obtener_personajes_disponibles()

            if not personajes_disponibles:
                print("⚠️ No hay personajes disponibles")
                self.buffer_ordenes.enqueue(orden)
                break

            for personaje in personajes_disponibles:
                prioridad = self.calcular_prioridad(orden, personaje)
                tarea = {
                    'orden': orden,
                    'personaje': personaje,
                    'prioridad': prioridad
                }
                self.cola_prioridades.enqueue(prioridad, tarea)
                self._tamanio_heap += 1

            ordenes_procesadas += 1

        self._despachar_acciones()

    def _obtener_personajes_disponibles(self):
        disponibles = []
        if hasattr(self.gestor, 'enanos_disponibles'):
            temp = []
            while not self.gestor.enanos_disponibles.empty():
                enano = self.gestor.enanos_disponibles.pop_front()
                if enano.esta_disponible():
                    disponibles.append(enano)
                temp.append(enano)
            for enano in temp:
                self.gestor.enanos_disponibles.push_back(enano)
        return disponibles

    def _despachar_acciones(self):
        acciones_despachadas = 0
        max_despachos = 3

        while acciones_despachadas < max_despachos:
            if self.cola_prioridades.is_empty():
                break

            prioridad, tarea = self.cola_prioridades.dequeue()
            self._tamanio_heap -= 1

            personaje = tarea['personaje']
            orden = tarea['orden']

            if not personaje.esta_disponible():
                continue

            self._ejecutar_accion(personaje, orden)
            acciones_despachadas += 1

            print(f"✅ {orden['accion']} por {personaje.tipo} (prioridad: {prioridad:.2f})")

    def _ejecutar_accion(self, personaje, orden):
        accion_tipo = orden['accion']

        if accion_tipo == 'comer':
            personaje.comer()
            self.acciones_ejecutadas.append({
                'personaje': personaje.tipo,
                'accion': 'comer',
                'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
            })
            return

        if accion_tipo == 'beber':
            # si vino con parametros de bebida, se los pasamos
            bebida = orden.get('parametros', {}).get('bebida')
            if bebida:
                personaje.beber(bebida, bar=self.bar)
            else:
                personaje.beber(bar=self.bar)
            self.acciones_ejecutadas.append({
                'personaje': personaje.tipo,
                'accion': 'beber',
                'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
            })
            return

        accion_info = {
            'tipo': orden['accion'],
            'duracion': self._calcular_duracion(orden['accion']),
            'parametros': orden.get('parametros', {})
        }

        if hasattr(self.gestor, 'marcar_ocupado'):
            self.gestor.marcar_ocupado(personaje, accion_info)
        else:
            personaje.asignar_accion(accion_info)

        self.acciones_ejecutadas.append({
            'personaje': personaje.tipo,
            'accion': orden['accion'],
            'timestamp': self.estado_juego.tiempo_actual if hasattr(self.estado_juego, 'tiempo_actual') else 0
        })

    def _calcular_duracion(self, accion):
        duraciones = {
            'minar': 10,
            'talar': 8,
            'construir': 15,
            'reparar': 12,
            'cultivar': 10,
            'defender': 5,
            'atacar': 5,
            'entrenar': 7,
            'dar_comida_animales': 5,
            'resguardar': 3,
            'comer': 2,
            'beber': 2
        }
        return duraciones.get(accion, 10)

    def ajustar_prioridades_por_evento(self, factor=0.8):
        try:
            for i, nodo in enumerate(self.cola_prioridades.heap):
                prioridad, tarea = nodo
                nueva_prioridad = max(1, int(prioridad * factor))
                change_priority(self.cola_prioridades, i, nueva_prioridad)
            print("🔁 Prioridades ajustadas por evento crítico")
        except Exception:
            pass

    def obtener_estadisticas(self):
        buffer_count = count(self.buffer_ordenes) if hasattr(self.buffer_ordenes, 'size') else 0
        return {
            'ordenes_en_buffer': buffer_count,
            'tareas_en_heap': self._tamanio_heap,
            'acciones_completadas': len(self.acciones_ejecutadas)
        }

    def mostrar_estado(self):
        stats = self.obtener_estadisticas()
        print("\n" + "=" * 50)
        print("📊 ESTADO DEL PLANIFICADOR")
        print("=" * 50)
        print(f"📥 Órdenes en buffer: {stats['ordenes_en_buffer']}")
        print(f"⚙️ Tareas en heap: {stats['tareas_en_heap']}")
        print(f"✅ Acciones completadas: {stats['acciones_completadas']}")
        print("=" * 50)
