# personajes.py 

from ListaEnlazada import LinkedList, to_list, find
from game_queue import Queue
from deque import Deque
import random
from enum import Enum


class ClasePersonaje(Enum):
    PRINCIPIANTE = 1
    INTERMEDIO = 2
    EXPERTO = 3


class EstadoPersonaje(Enum):
    VIVO = 1
    MUERTO = 2
    HERIDO = 3


class Sentimiento(Enum):
    FELIZ = 1
    TRISTE = 2
    ENOJADO = 3
    CANSADO = 4


class Personaje:
    """
    Personaje base SIN inventario individual.
    En tu GUI todos dejan los recursos en cofres globales.
    """
    def __init__(self, tipo, simbolo, posicion=(0, 0)):
        self.tipo = tipo
        self.simbolo = simbolo
        self.posicion = posicion
        self.clase = ClasePersonaje.PRINCIPIANTE
        self.nivel = 1
        self.experiencia = 0
        self.estado = EstadoPersonaje.VIVO
        self.salud = 100
        self.energia = 100
        self.hambre = 0
        self.sed = 0
        self.sentimiento = Sentimiento.FELIZ
        self.oficio = tipo
        self.accion_actual = None
        self.tiempo_ocupado = 0  # lo puede usar el gestor / planificador

    # =========================================================
    # utilidades
    # =========================================================
    def calcular_compatibilidad(self, tipo_accion):
        # base: todos = 1
        return 1.0

    def ganar_experiencia(self, puntos):
        self.experiencia += puntos
        if self.experiencia >= 100:
            self.subir_nivel()
            self.experiencia = 0

    def subir_nivel(self):
        self.nivel += 1
        if self.nivel == 2:
            self.clase = ClasePersonaje.INTERMEDIO
        elif self.nivel >= 3:
            self.clase = ClasePersonaje.EXPERTO

    def esta_vivo(self):
        return self.estado == EstadoPersonaje.VIVO

    def morir(self, causa="desconocida"):
        self.estado = EstadoPersonaje.MUERTO
        self.salud = 0

    def recibir_lesion(self, causa=""):
        if not self.esta_vivo():
            return
        self.salud -= 20
        if self.salud <= 0:
            self.morir(causa)
        else:
            self.estado = EstadoPersonaje.HERIDO

    # =========================================================
    # acciones básicas
    # =========================================================
    def asignar_accion(self, accion):
        # accion = {'accion': 'minar', 'duracion': 60, ...}
        self.accion_actual = accion
        self.tiempo_ocupado = accion.get('duracion', 0)

    def completar_accion(self):
        acc = self.accion_actual
        self.accion_actual = None
        self.tiempo_ocupado = 0
        return acc

    def comer(self):
        if not self.esta_vivo():
            return False
        # sin inventario, solo curamos un poco
        self.hambre = 0
        self.salud = min(100, self.salud + 20)
        return True

    def beber(self):
        if not self.esta_vivo():
            return False
        self.sed = 0
        self.energia = min(100, self.energia + 10)
        return True

    def descansar(self):
        self.energia = min(100, self.energia + 30)
        if self.salud < 100:
            self.salud += 5

    def mover_a(self, nueva_pos):
        self.posicion = nueva_pos

    def __repr__(self):
        return f"<{self.tipo} nv{self.nivel} ({self.salud}hp)>"


# =========================================================
# PERSONAJES QUE SÍ TIENES EN TU GUI
# =========================================================

class Enano(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Enano', '⚔️', posicion)
        self.defensa = 10

    def calcular_compatibilidad(self, tipo_accion):
        # enanos buenos para defender/pelear duendes
        if tipo_accion in ('defender', 'pelear'):
            return 15 * self.clase.value
        return 5 * self.clase.value

    def defender(self, enemigo=None):
        if not self.esta_vivo():
            return False
        self.energia -= 10
        self.ganar_experiencia(15)
        return True


class Minero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Minero', '⛏️', posicion)
        self.materiales_minados = 0

    def calcular_compatibilidad(self, tipo_accion):
        if tipo_accion == 'minar':
            return 12 * self.clase.value
        if tipo_accion == 'construir':
            return 4 * self.clase.value
        return 1

    def minar(self):
        if not self.esta_vivo():
            return None
        cantidad = random.randint(2, 5)
        self.materiales_minados += cantidad
        self.energia -= 15
        self.ganar_experiencia(10)
        # GUI lo mete al cofre
        return {'recurso': 'piedra', 'cantidad': cantidad}


class Lenador(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Leñador', '🪓', posicion)
        self.arboles_talados = 0

    def calcular_compatibilidad(self, tipo_accion):
        if tipo_accion == 'talar':
            return 12 * self.clase.value
        return 1

    def talar(self):
        if not self.esta_vivo():
            return None
        cantidad = random.randint(1, 4)
        self.arboles_talados += 1
        self.energia -= 12
        self.ganar_experiencia(8)
        return {'recurso': 'madera', 'cantidad': cantidad}


class Granjero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Granjero', '👨‍🌾', posicion)
        self.cultivos_plantados = 0

    def calcular_compatibilidad(self, tipo_accion):
        if tipo_accion in ('plantar', 'cosechar', 'ordeñar', 'huevos'):
            return 10 * self.clase.value
        return 1

    def plantar(self):
        if not self.esta_vivo():
            return None
        self.cultivos_plantados += 1
        self.energia -= 10
        self.ganar_experiencia(6)
        return {'cultivo': 'trigo', 'cantidad': 1}

    def cosechar(self):
        if not self.esta_vivo():
            return None
        self.energia -= 8
        self.ganar_experiencia(6)
        return {'recurso': 'trigo', 'cantidad': 1}

    def ordeñar(self):
        if not self.esta_vivo():
            return None
        self.energia -= 5
        self.ganar_experiencia(4)
        return {'recurso': 'leche', 'cantidad': 1}

    def recoger_huevos(self):
        if not self.esta_vivo():
            return None
        self.energia -= 4
        self.ganar_experiencia(4)
        return {'recurso': 'huevos', 'cantidad': 1}


class Constructor(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Constructor', '🏗', posicion)

    def calcular_compatibilidad(self, tipo_accion):
        if tipo_accion in ('construir', 'reparar'):
            return 10 * self.clase.value
        return 1

    def construir(self):
        if not self.esta_vivo():
            return None
        self.energia -= 20
        self.ganar_experiencia(12)
        return {'construccion': 'edificio', 'resultado': 'ok'}

    def reparar(self):
        if not self.esta_vivo():
            return None
        self.energia -= 10
        self.ganar_experiencia(8)
        return {'accion': 'reparar', 'resultado': 'ok'}


# =========================================================
# ENEMIGO QUE SÍ USA TU JUEGO (DUENDE), PERO SIN INVENTARIO
# =========================================================

class Duende:
    def __init__(self, posicion=(0, 0)):
        self.tipo = 'Duende'
        self.simbolo = '👹'
        self.posicion = posicion
        self.poder_ataque = random.randint(10, 25)
        self.salud = 40

    def robar_de(self, cofre):
        if cofre is None:
            return None
        item = cofre.retirar_cualquiera()
        return item

    def recibir_dano(self, cantidad):
        self.salud -= cantidad
        if self.salud <= 0:
            self.salud = 0


# =========================================================
# COFRES (globales)
# =========================================================

class CofrePrincipal:
    """
    Cofre global de recursos para todos los personajes.
    """
    def __init__(self):
        self.tipo = 'Cofre Principal'
        self.cola_recursos = Queue()
        self.cola_herramientas = Queue()
        self.recursos_dict = {}
        self.herramientas_dict = {}
        self.capacidad = 200

    def inicializar_herramientas(self):
        herramientas = {'pico': 3, 'hacha': 3, 'martillo': 2, 'azada': 2}
        for h, cant in herramientas.items():
            self.guardar_herramienta(h, cant)

    def guardar(self, recurso, cantidad):
        total = 0
        for val in self.recursos_dict.values():
            total += val
        if total + cantidad > self.capacidad:
            return False
        for _ in range(cantidad):
            item = {'tipo': recurso, 'cantidad': 1}
            self.cola_recursos.enqueue(item)
        if recurso not in self.recursos_dict:
            self.recursos_dict[recurso] = 0
        self.recursos_dict[recurso] += cantidad
        return True

    def guardar_herramienta(self, herramienta, cantidad, de_personaje=None):
        # aquí quitamos lo de "Orco no puede guardar"
        if de_personaje and hasattr(de_personaje, 'tipo'):
            if de_personaje.tipo == 'Duende':
                return False
        for _ in range(cantidad):
            item = {'tipo': herramienta, 'cantidad': 1}
            self.cola_herramientas.enqueue(item)
        if herramienta not in self.herramientas_dict:
            self.herramientas_dict[herramienta] = 0
        self.herramientas_dict[herramienta] += cantidad
        return True

    def retirar(self, recurso, cantidad):
        if self.recursos_dict.get(recurso, 0) < cantidad:
            return False
        temp = Queue()
        retirados = 0
        while not self.cola_recursos.empty():
            item = self.cola_recursos.dequeue()
            if item['tipo'] == recurso and retirados < cantidad:
                retirados += 1
            else:
                temp.enqueue(item)
        while not temp.empty():
            self.cola_recursos.enqueue(temp.dequeue())
        self.recursos_dict[recurso] -= cantidad
        if self.recursos_dict[recurso] == 0:
            del self.recursos_dict[recurso]
        return True

    def retirar_cualquiera(self):
        if self.cola_recursos.empty():
            return None
        item = self.cola_recursos.dequeue()
        tipo = item['tipo']
        self.recursos_dict[tipo] -= 1
        if self.recursos_dict[tipo] == 0:
            del self.recursos_dict[tipo]
        return item

    def ver_inventario(self):
        return {
            'recursos': dict(self.recursos_dict),
            'herramientas': dict(self.herramientas_dict)
        }


class CofreAlimentos:
    def __init__(self):
        self.cola = Queue()
        self.comidas = {}
        self.capacidad = 100

    def guardar_comida(self, tipo, cantidad):
        total = 0
        for val in self.comidas.values():
            total += val
        if total + cantidad > self.capacidad:
            return False
        for _ in range(cantidad):
            self.cola.enqueue({'tipo': tipo, 'cantidad': 1})
        if tipo not in self.comidas:
            self.comidas[tipo] = 0
        self.comidas[tipo] += cantidad
        return True

    def retirar(self, tipo, cantidad):
        if self.comidas.get(tipo, 0) < cantidad:
            return False
        temp = Queue()
        retirados = 0
        while not self.cola.empty():
            item = self.cola.dequeue()
            if item['tipo'] == tipo and retirados < cantidad:
                retirados += 1
            else:
                temp.enqueue(item)
        while not temp.empty():
            self.cola.enqueue(temp.dequeue())
        self.comidas[tipo] -= cantidad
        if self.comidas[tipo] == 0:
            del self.comidas[tipo]
        return True

    def retirar_cualquiera(self):
        if self.cola.empty():
            return None
        item = self.cola.dequeue()
        t = item['tipo']
        self.comidas[t] -= 1
        if self.comidas[t] == 0:
            del self.comidas[t]
        return item


class Bar:
    def __init__(self):
        self.bebidas = {'cerveza': 10, 'agua': 20}

    def servir_bebida(self, tipo):
        if tipo not in self.bebidas or self.bebidas[tipo] == 0:
            return False
        self.bebidas[tipo] -= 1
        return True
