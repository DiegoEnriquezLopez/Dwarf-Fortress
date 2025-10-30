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
    VIVO = "vivo"
    LESIONADO = "lesionado"
    MUERTO = "muerto"


class Sentimiento(Enum):
    FELIZ = "feliz"
    TRISTE = "triste"
    ENOJADO = "enojado"


class Personaje:
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
        self.tiempo_ocupado = 0
        self.inventario = LinkedList()

    def calcular_compatibilidad(self, tipo_accion):
        return 1.0

    def ganar_experiencia(self, puntos):
        self.experiencia += puntos
        if self.experiencia >= 100 and self.clase == ClasePersonaje.PRINCIPIANTE:
            self.clase = ClasePersonaje.INTERMEDIO
            self.nivel = 2
            self.experiencia = 0
            self.sentimiento = Sentimiento.FELIZ
        elif self.experiencia >= 200 and self.clase == ClasePersonaje.INTERMEDIO:
            self.clase = ClasePersonaje.EXPERTO
            self.nivel = 3
            self.experiencia = 0
            self.sentimiento = Sentimiento.FELIZ

    def recibir_lesion(self, descripcion, es_mortal=False):
        if self.estado == EstadoPersonaje.MUERTO:
            return
        if es_mortal:
            self.morir(descripcion)
        else:
            self.salud -= 30
            self.sentimiento = Sentimiento.TRISTE
            if self.salud <= 0:
                self.morir(descripcion)
            else:
                self.estado = EstadoPersonaje.LESIONADO

    def morir(self, causa):
        self.estado = EstadoPersonaje.MUERTO
        self.salud = 0

    def esta_vivo(self):
        return self.estado != EstadoPersonaje.MUERTO

    def esta_disponible(self):
        return self.esta_vivo() and self.energia > 20 and self.accion_actual is None

    def asignar_accion(self, accion):
        self.accion_actual = accion
        self.tiempo_ocupado = accion.get('duracion', 10)

    def completar_accion(self):
        resultado = self.accion_actual
        self.accion_actual = None
        self.tiempo_ocupado = 0
        self.ganar_experiencia(5)
        return resultado

    def actualizar_necesidades(self):
        self.hambre = min(100, self.hambre + 2)
        self.sed = min(100, self.sed + 3)
        if self.hambre > 80 or self.sed > 80:
            self.sentimiento = Sentimiento.ENOJADO
        elif self.hambre > 60 or self.sed > 60:
            self.sentimiento = Sentimiento.TRISTE
        elif self.hambre < 30 and self.sed < 30:
            self.sentimiento = Sentimiento.FELIZ

    def tiene_en_inventario(self, item):
        encontrados = find(self.inventario, lambda d: d == item)
        return len(encontrados) > 0

    def comer(self, cofre_alimentos=None):
        if not self.esta_vivo():
            return False
        comio = False
        if self.tiene_en_inventario("trigo") or self.tiene_en_inventario("carne"):
            self.salud = min(100, self.salud + 20)
            self.hambre = max(0, self.hambre - 40)
            self.sentimiento = Sentimiento.FELIZ
            comio = True
        elif cofre_alimentos is not None and cofre_alimentos.retirar('carne', 1):
            self.salud = min(100, self.salud + 20)
            self.hambre = max(0, self.hambre - 40)
            self.sentimiento = Sentimiento.FELIZ
            comio = True
        if comio:
            return True
        return False

    def beber(self, tipo_bebida='agua', bar=None):
        if not self.esta_vivo():
            return False

        if tipo_bebida == 'cerveza' and self.sed > 20:
            tiene_agua_inv = self.tiene_en_inventario('agua')
            tiene_agua_bar = (bar is not None and bar.servir_bebida('agua'))
            if tiene_agua_inv or tiene_agua_bar:
                tipo_bebida = 'agua'

        bebio = False

        if tipo_bebida == 'cerveza':
            if self.tiene_en_inventario('cerveza'):
                self.energia = min(100, self.energia + 15)  
                self.sentimiento = Sentimiento.FELIZ
                bebio = True
            elif bar is not None and bar.servir_bebida('cerveza'):
                self.energia = min(100, self.energia + 15)
                self.sentimiento = Sentimiento.FELIZ
                bebio = True

        elif tipo_bebida == 'agua':
            if self.tiene_en_inventario('agua'):
                self.sed = max(0, self.sed - 40)      
                self.energia = min(100, self.energia + 8)  
                bebio = True
            elif bar is not None and bar.servir_bebida('agua'):
                self.sed = max(0, self.sed - 40)
                self.energia = min(100, self.energia + 8)
                bebio = True
                
        if not bebio:
            return False
        return True

    def descansar(self):
        self.energia = min(100, self.energia + 30)

    def agregar_a_inventario(self, item):
        self.inventario.add(item)

    def obtener_inventario(self):
        return to_list(self.inventario)

    def __repr__(self):
        return f"{self.simbolo} {self.tipo} ({self.clase.name}) Nv.{self.nivel} [{self.sentimiento.value}]"


class Minero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Minero', '⛏️', posicion)
        self.materiales_minados = 0
        self._actualizar_stats()

    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'eficiencia': 1.0},
            ClasePersonaje.INTERMEDIO: {'eficiencia': 1.5},
            ClasePersonaje.EXPERTO: {'eficiencia': 2.0}
        }
        self.eficiencia = stats[self.clase]['eficiencia']

    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {'minar': 10, 'construir': 3}
        return compatibilidades.get(tipo_accion, 1) * self.clase.value

    def minar(self):
        if not self.esta_vivo():
            return None
        if random.random() < 0.05:
            self.morir("asfixia")
            return None
        if random.random() < 0.03:
            self.morir("intoxicación")
            return None
        cantidad = int(random.randint(2, 5) * self.eficiencia)
        self.materiales_minados += cantidad
        self.energia -= 15
        self.ganar_experiencia(10)
        self._actualizar_stats()
        for _ in range(cantidad):
            self.agregar_a_inventario('piedra')
        return {'recurso': 'piedra', 'cantidad': cantidad}


class Lenador(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Leñador', '🪓', posicion)
        self.arboles_talados = 0
        self._actualizar_stats()

    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'eficiencia': 1.0},
            ClasePersonaje.INTERMEDIO: {'eficiencia': 1.5},
            ClasePersonaje.EXPERTO: {'eficiencia': 2.0}
        }
        self.eficiencia = stats[self.clase]['eficiencia']

    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {'talar': 10, 'construir': 4}
        return compatibilidades.get(tipo_accion, 1) * self.clase.value

    def talar(self):
        if not self.esta_vivo():
            return None
        if random.random() < 0.07:
            self.morir("árbol caído encima")
            return None
        if random.random() < 0.10:
            self.recibir_lesion("corte con hacha")
        cantidad = int(random.randint(3, 6) * self.eficiencia)
        self.arboles_talados += 1
        self.energia -= 15
        self.ganar_experiencia(8)
        self._actualizar_stats()
        for _ in range(cantidad):
            self.agregar_a_inventario('madera')
        return {'recurso': 'madera', 'cantidad': cantidad}


class Constructor(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Constructor', '🔨', posicion)
        self.estructuras_construidas = 0
        self._actualizar_stats()

    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'precision': 0.7},
            ClasePersonaje.INTERMEDIO: {'precision': 0.85},
            ClasePersonaje.EXPERTO: {'precision': 0.95}
        }
        self.precision = stats[self.clase]['precision']

    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {'construir': 10, 'reparar': 9}
        return compatibilidades.get(tipo_accion, 1) * self.clase.value

    def construir(self, tipo_estructura='edificio'):
        if not self.esta_vivo():
            return None
        if random.random() < (1 - self.precision) * 0.3:
            self.recibir_lesion("golpe con martillo")
        tiempo = max(1, 10 - (self.clase.value * 2))
        self.estructuras_construidas += 1
        self.energia -= 20
        self.ganar_experiencia(15)
        self._actualizar_stats()
        return {'estructura': tipo_estructura, 'tiempo': tiempo}


class Granjero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Granjero', '👨‍🌾', posicion)
        self.cultivos_plantados = 0
        self._actualizar_stats()

    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'eficiencia': 1.0},
            ClasePersonaje.INTERMEDIO: {'eficiencia': 1.5},
            ClasePersonaje.EXPERTO: {'eficiencia': 2.0}
        }
        self.eficiencia = stats[self.clase]['eficiencia']

    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {'cultivar': 10, 'dar_comida_animales': 10}
        return compatibilidades.get(tipo_accion, 1) * self.clase.value

    def cultivar(self, tipo_cultivo='trigo'):
        if not self.esta_vivo():
            return None
        cantidad = int(random.randint(4, 8) * self.eficiencia)
        self.cultivos_plantados += 1
        self.energia -= 15
        self.ganar_experiencia(7)
        self._actualizar_stats()
        for _ in range(cantidad):
            self.agregar_a_inventario(tipo_cultivo)
        return {'cultivo': tipo_cultivo, 'cantidad': cantidad}

    def dar_comida_animales(self, animales, trigo_disponible):
        if not self.esta_vivo():
            return False
        trigo_necesario = len(animales)
        if trigo_disponible < trigo_necesario:
            return False
        for a in animales:
            if hasattr(a, 'comer'):
                a.comer()
        self.energia -= 10
        return True


class Enano(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Enano', '🧔', posicion)
        self.fuerza = 5
        self._actualizar_stats()

    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'ataque': 6},
            ClasePersonaje.INTERMEDIO: {'ataque': 10},
            ClasePersonaje.EXPERTO: {'ataque': 14}
        }
        self.ataque = stats[self.clase]['ataque']

    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {'defender': 10, 'entrenar': 10}
        return compatibilidades.get(tipo_accion, 1) * self.clase.value

    def entrenar(self):
        if not self.esta_vivo():
            return False
        self.fuerza += 1 * self.clase.value
        self.energia -= 20
        self.ganar_experiencia(5)
        self.sentimiento = Sentimiento.FELIZ
        return True

    def defender(self, enemigo):
        if not self.esta_vivo():
            return False
        poder_enano = self.fuerza * self.clase.value
        poder_enemigo = enemigo.poder_ataque
        if poder_enano >= poder_enemigo:
            enemigo.recibir_dano(poder_enano)
            self.ganar_experiencia(20)
            self.sentimiento = Sentimiento.FELIZ
            return True
        else:
            diferencia = poder_enemigo - poder_enano
            if diferencia > 30:
                self.morir(f"ataque de {enemigo.tipo}")
            else:
                self.recibir_lesion(f"ataque de {enemigo.tipo}")
            return False


class Duende:
    def __init__(self, posicion=(0, 0)):
        self.tipo = 'Duende'
        self.simbolo = '👹'
        self.posicion = posicion
        self.poder_ataque = random.randint(20, 35)
        self.salud = 50
        self.objetos_robados = []

    def atacar(self, victima):
        if self.salud <= 0:
            return False
        if random.random() < 0.3:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        return True

    def robar(self, cofre):
        if self.salud <= 0 or not hasattr(cofre, 'recursos_dict'):
            return None
        if not cofre.recursos_dict:
            return None
        item = random.choice(list(cofre.recursos_dict.keys()))
        cantidad = random.randint(1, min(3, cofre.recursos_dict[item]))
        if cofre.retirar(item, cantidad):
            self.objetos_robados.append((item, cantidad))
            return (item, cantidad)
        return None

    def recibir_dano(self, cantidad):
        self.salud -= cantidad
        if self.salud <= 0:
            pass


class Orco:
    def __init__(self, posicion=(0, 0)):
        self.tipo = 'Orco'
        self.simbolo = '👺'
        self.posicion = posicion
        self.poder_ataque = random.randint(35, 50)
        self.salud = 80

    def atacar(self, victima):
        if self.salud <= 0:
            return False
        if random.random() < 0.5:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        return True

    def recibir_dano(self, cantidad):
        self.salud -= cantidad
        if self.salud <= 0:
            pass


class Vaca:
    def __init__(self):
        self.tipo = 'Vaca'
        self.simbolo = '🐄'
        self.hambre = 0
        self.sed = 0
        self.viva = True
        self.leche_disponible = 0

    def comer(self):
        if not self.viva:
            return False
        self.hambre = max(0, self.hambre - 50)
        self.leche_disponible += 1
        return True

    def beber(self):
        if not self.viva:
            return False
        self.sed = max(0, self.sed - 50)
        return True

    def dar_leche(self):
        if not self.viva or self.hambre > 50 or self.sed > 50:
            return 0
        leche = self.leche_disponible
        self.leche_disponible = 0
        return leche

    def sacrificar(self):
        if not self.viva:
            return None
        self.viva = False
        return {'carne': 10, 'piel': 5}

    def actualizar(self):
        if self.viva:
            self.hambre = min(100, self.hambre + 15)
            self.sed = min(100, self.sed + 10)
            if self.hambre >= 100 or self.sed >= 100:
                self.viva = False


class Gallina:
    def __init__(self):
        self.tipo = 'Gallina'
        self.simbolo = '🐔'
        self.hambre = 0
        self.sed = 0
        self.viva = True

    def comer(self):
        if not self.viva:
            return False
        self.hambre = max(0, self.hambre - 50)
        return True

    def beber(self):
        if not self.viva:
            return False
        self.sed = max(0, self.sed - 50)
        return True

    def poner_huevo(self):
        if not self.viva or self.hambre > 50 or self.sed > 50:
            return 0
        huevos = random.randint(1, 3)
        return huevos

    def sacrificar(self):
        if not self.viva:
            return None
        self.viva = False
        return {'carne': 2, 'plumas': 5}

    def actualizar(self):
        if self.viva:
            self.hambre = min(100, self.hambre + 20)
            self.sed = min(100, self.sed + 15)
            if self.hambre >= 100 or self.sed >= 100:
                self.viva = False


class Cerdo:
    def __init__(self):
        self.tipo = 'Cerdo'
        self.simbolo = '🐷'
        self.hambre = 0
        self.sed = 0
        self.vivo = True

    def comer(self):
        if not self.vivo:
            return False
        self.hambre = max(0, self.hambre - 50)
        return True

    def beber(self):
        if not self.vivo:
            return False
        self.sed = max(0, self.sed - 50)
        return True

    def sacrificar(self):
        if not self.vivo:
            return None
        self.vivo = False
        return {'carne': 6, 'piel': 2}

    def actualizar(self):
        if self.vivo:
            self.hambre = min(100, self.hambre + 18)
            self.sed = min(100, self.sed + 12)
            if self.hambre >= 100 or self.sed >= 100:
                self.vivo = False


class Trigo:
    def __init__(self):
        self.tipo = 'trigo'
        self.crecimiento = 0
        self.maduro = False

    def crecer(self, hay_lluvia=False):
        if self.maduro:
            return
        incremento = 30 if hay_lluvia else 15
        self.crecimiento = min(100, self.crecimiento + incremento)
        if self.crecimiento >= 100:
            self.maduro = True

    def cosechar(self):
        if not self.maduro:
            return 0
        cantidad = random.randint(5, 10)
        self.maduro = False
        self.crecimiento = 0
        return cantidad


class CofrePrincipal:
    def __init__(self):
        self.tipo = 'Cofre Principal'
        self.cola_recursos = Queue()
        self.cola_herramientas = Queue()
        self.recursos_dict = {}
        self.herramientas_dict = {}
        self.capacidad = 200

    def inicializar_herramientas(self):
        herramientas = {'pico': 3, 'hacha': 3, 'martillo': 2, 'azada': 2, 'espada': 2}
        for h, cant in herramientas.items():
            self.guardar_herramienta(h, cant)

    def guardar(self, recurso, cantidad):
        total = sum(self.recursos_dict.values())
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
        if de_personaje and hasattr(de_personaje, 'tipo'):
            if de_personaje.tipo in ['Duende', 'Orco']:
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
        while not self.cola_recursos.empty() and retirados < cantidad:
            item = self.cola_recursos.dequeue()
            if item['tipo'] == recurso:
                retirados += 1
            else:
                temp.enqueue(item)
        while not self.cola_recursos.empty():
            temp.enqueue(self.cola_recursos.dequeue())
        while not temp.empty():
            self.cola_recursos.enqueue(temp.dequeue())
        self.recursos_dict[recurso] -= cantidad
        if self.recursos_dict[recurso] == 0:
            del self.recursos_dict[recurso]
        return True

    def ver_inventario(self):
        return {
            'recursos': dict(self.recursos_dict),
            'herramientas': dict(self.herramientas_dict)
        }


class CofreAlimentos:
    def __init__(self):
        self.tipo = 'Cofre Alimentos'
        self.cola_alimentos = Deque()
        self.alimentos_dict = {}
        self.capacidad = 100

    def guardar(self, alimento, cantidad):
        items_permitidos = ['carne', 'huevos', 'leche', 'trigo', 'pan', 'plumas', 'piel', 'cerveza', 'agua']
        if alimento not in items_permitidos:
            return False
        total = sum(self.alimentos_dict.values())
        if total + cantidad > self.capacidad:
            return False
        for _ in range(cantidad):
            item = {'tipo': alimento, 'frescura': 100}
            self.cola_alimentos.push_back(item)
        if alimento not in self.alimentos_dict:
            self.alimentos_dict[alimento] = 0
        self.alimentos_dict[alimento] += cantidad
        return True

    def retirar(self, alimento, cantidad):
        if self.alimentos_dict.get(alimento, 0) < cantidad:
            return False
        temp = Deque()
        retirados = 0
        while not self.cola_alimentos.empty() and retirados < cantidad:
            item = self.cola_alimentos.pop_front()
            if item['tipo'] == alimento:
                retirados += 1
            else:
                temp.push_back(item)
        while not self.cola_alimentos.empty():
            temp.push_back(self.cola_alimentos.pop_front())
        while not temp.empty():
            self.cola_alimentos.push_back(temp.pop_front())
        self.alimentos_dict[alimento] -= cantidad
        if self.alimentos_dict[alimento] == 0:
            del self.alimentos_dict[alimento]
        return True

    def actualizar_frescura(self):
        temp = Deque()
        while not self.cola_alimentos.empty():
            item = self.cola_alimentos.pop_front()
            item['frescura'] -= 10
            if item['frescura'] <= 0:
                self.alimentos_dict[item['tipo']] -= 1
                if self.alimentos_dict[item['tipo']] == 0:
                    del self.alimentos_dict[item['tipo']]
            else:
                temp.push_back(item)
        while not temp.empty():
            self.cola_alimentos.push_back(temp.pop_front())

    def ver_inventario(self):
        return dict(self.alimentos_dict)


class Lluvia:
    def __init__(self):
        self.tipo = 'Lluvia'
        self.simbolo = '🌧️'
        self.activa = False

    def activar(self):
        self.activa = True

    def aplicar_efectos(self, cultivos):
        if not self.activa:
            return
        for cultivo in cultivos:
            cultivo.crecer(hay_lluvia=True)

    def detener(self):
        self.activa = False


class Tormenta:
    def __init__(self):
        self.tipo = 'Tormenta'
        self.simbolo = '⛈️'
        self.activa = False
        self.intensidad = 0

    def activar(self, intensidad=5):
        self.activa = True
        self.intensidad = intensidad

    def aplicar_efectos(self, personajes):
        if not self.activa:
            return
        prob_rayo = self.intensidad * 0.1
        if random.random() < prob_rayo and personajes:
            victima = random.choice(personajes)
            if victima.esta_vivo():
                victima.morir("impacto de rayo")
        prob_inundacion = self.intensidad * 0.08
        if random.random() < prob_inundacion and personajes:
            afectados = random.sample(personajes, min(len(personajes), 3))
            for personaje in afectados:
                if personaje.esta_vivo():
                    personaje.recibir_lesion("inundación")

    def detener(self):
        self.activa = False


class Tornado:
    def __init__(self):
        self.tipo = 'Tornado'
        self.simbolo = '🌪️'
        self.activo = False

    def activar(self):
        self.activo = True

    def aplicar_efectos(self, personajes, animales, estructuras):
        if not self.activo:
            return
        for animal in animales:
            if hasattr(animal, 'viva'):
                if animal.viva and random.random() < 0.6:
                    animal.viva = False
            elif hasattr(animal, 'vivo'):
                if animal.vivo and random.random() < 0.6:
                    animal.vivo = False
        for estructura in estructuras:
            if random.random() < 0.7:
                estructura['destruida'] = True
        for personaje in personajes:
            if personaje.esta_vivo() and random.random() < 0.4:
                personaje.morir("tornado")

    def detener(self):
        self.activo = False
