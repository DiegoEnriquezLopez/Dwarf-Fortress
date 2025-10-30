from enum import Enum
try:
    from ListaEnlazada import LinkedList, to_list, find, length, iterate
except ImportError:
    from lista_enlazada import LinkedList, to_list, find, length, iterate

try:
    from game_queue import Queue, count, clear, queue_extend
except ImportError:
    pass

try:
    from deque import Deque
except ImportError:
    pass

import random
from enum import Enum


# ============= ENUMERACIONES =============
class ClasePersonaje(Enum):
    PRINCIPIANTE = 1
    INTERMEDIO = 2
    EXPERTO = 3


class EstadoPersonaje(Enum):
    VIVO = "vivo"
    LESIONADO = "lesionado"
    MUERTO = "muerto"


# ============= CLASE BASE PERSONAJE =============
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
        self.moral = 100
        self.oficio = tipo
        self.accion_actual = None
        self.tiempo_ocupado = 0
        self.inventario = LinkedList()
    
    def calcular_compatibilidad(self, tipo_accion):
        """Compatibilidad base (sobrescribir en subclases)"""
        return 1.0
    
    def ganar_experiencia(self, puntos):
        self.experiencia += puntos
        if self.experiencia >= 100 and self.clase == ClasePersonaje.PRINCIPIANTE:
            self.clase = ClasePersonaje.INTERMEDIO
            self.nivel = 2
            self.experiencia = 0
            print(f"⬆️ {self.tipo} subió a INTERMEDIO")
        elif self.experiencia >= 200 and self.clase == ClasePersonaje.INTERMEDIO:
            self.clase = ClasePersonaje.EXPERTO
            self.nivel = 3
            self.experiencia = 0
            print(f"⬆️ {self.tipo} subió a EXPERTO")
    
    def recibir_lesion(self, descripcion, es_mortal=False):
        if self.estado == EstadoPersonaje.MUERTO:
            return
        if es_mortal:
            self.morir(descripcion)
        else:
            self.salud -= 30
            if self.salud <= 0:
                self.morir(descripcion)
            else:
                self.estado = EstadoPersonaje.LESIONADO
                print(f"🩹 {self.tipo} lesionado por {descripcion}")
    
    def morir(self, causa):
        self.estado = EstadoPersonaje.MUERTO
        self.salud = 0
        print(f"💀 {self.tipo} murió por {causa}")
    
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
        if self.hambre > 70 or self.sed > 70:
            self.moral = max(0, self.moral - 2)
    
    def comer(self):
        if not self.esta_vivo():
            return False
        self.salud = min(100, self.salud + 20)
        self.hambre = max(0, self.hambre - 30)
        print(f"🍖 {self.tipo} comió")
        return True
    
    def descansar(self):
        self.energia = min(100, self.energia + 30)
    
    def agregar_a_inventario(self, item):
        self.inventario.add(item)
    
    def obtener_inventario(self):
        return to_list(self.inventario)
    
    def __repr__(self):
        return f"{self.simbolo} {self.tipo} ({self.clase.name}) Nv.{self.nivel}"


# ============= MINERO =============
class Minero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Minero', '⛏️', posicion)
        self.materiales_minados = 0
        self._actualizar_stats()
    
    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'minar': 10, 'velocidad': 1.0},
            ClasePersonaje.INTERMEDIO: {'minar': 15, 'velocidad': 1.5},
            ClasePersonaje.EXPERTO: {'minar': 20, 'velocidad': 2.0}
        }
        self.habilidad_minar = stats[self.clase]['minar']
        self.velocidad = stats[self.clase]['velocidad']
    
    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {
            'minar': 10,
            'construir': 5,
            'defender': 3,
            'talar': 2,
            'cultivar': 1
        }
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
        
        cantidad = random.randint(2, 5) * int(self.habilidad_minar * self.velocidad / 10)
        self.materiales_minados += cantidad
        self.ganar_experiencia(10)
        self._actualizar_stats()
        
        for _ in range(cantidad):
            self.agregar_a_inventario('piedra')
        
        print(f"⛏️ {self.tipo} minó {cantidad} piedras")
        return {'recurso': 'piedra', 'cantidad': cantidad}


# ============= LEÑADOR =============
class Lenador(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Leñador', '🪓', posicion)
        self.arboles_talados = 0
        self._actualizar_stats()
    
    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'talar': 10, 'velocidad': 1.0},
            ClasePersonaje.INTERMEDIO: {'talar': 15, 'velocidad': 1.5},
            ClasePersonaje.EXPERTO: {'talar': 20, 'velocidad': 2.0}
        }
        self.habilidad_talar = stats[self.clase]['talar']
        self.velocidad = stats[self.clase]['velocidad']
    
    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {
            'talar': 10,
            'construir': 6,
            'recolectar': 4,
            'minar': 2,
            'defender': 2
        }
        return compatibilidades.get(tipo_accion, 1) * self.clase.value
    
    def talar(self):
        if not self.esta_vivo():
            return None
        
        if random.random() < 0.07:
            self.morir("árbol caído")
            return None
        if random.random() < 0.10:
            self.recibir_lesion("corte con hacha")
        
        cantidad = random.randint(3, 6) * int(self.habilidad_talar * self.velocidad / 10)
        self.arboles_talados += 1
        self.ganar_experiencia(8)
        self._actualizar_stats()
        
        for _ in range(cantidad):
            self.agregar_a_inventario('madera')
        
        print(f"🪓 {self.tipo} taló {cantidad} maderas")
        return {'recurso': 'madera', 'cantidad': cantidad}


# ============= CONSTRUCTOR =============
class Constructor(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Constructor', '🔨', posicion)
        self.estructuras_construidas = 0
        self._actualizar_stats()
    
    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'construir': 10, 'precision': 0.7},
            ClasePersonaje.INTERMEDIO: {'construir': 15, 'precision': 0.85},
            ClasePersonaje.EXPERTO: {'construir': 20, 'precision': 0.95}
        }
        self.habilidad_construir = stats[self.clase]['construir']
        self.precision = stats[self.clase]['precision']
    
    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {
            'construir': 10,
            'reparar': 9,
            'minar': 5,
            'talar': 4,
            'defender': 2
        }
        return compatibilidades.get(tipo_accion, 1) * self.clase.value
    
    def construir(self, tipo_estructura='edificio'):
        if not self.esta_vivo():
            return None
        
        if random.random() < (1 - self.precision) * 0.3:
            self.recibir_lesion("golpe martillo")
        
        tiempo = max(1, 10 - (self.clase.value * 2))
        self.estructuras_construidas += 1
        self.ganar_experiencia(15)
        self._actualizar_stats()
        
        print(f"🔨 {self.tipo} construyó {tipo_estructura}")
        return {'estructura': tipo_estructura, 'tiempo': tiempo}


# ============= GRANJERO =============
class Granjero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Granjero', '👨‍🌾', posicion)
        self.cultivos_plantados = 0
        self._actualizar_stats()
    
    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'cultivar': 8},
            ClasePersonaje.INTERMEDIO: {'cultivar': 12},
            ClasePersonaje.EXPERTO: {'cultivar': 16}
        }
        self.habilidad_cultivar = stats[self.clase]['cultivar']
    
    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {
            'cultivar': 10,
            'recolectar': 9,
            'cazar': 4,
            'construir': 3
        }
        return compatibilidades.get(tipo_accion, 1) * self.clase.value
    
    def cultivar(self, tipo_cultivo='trigo'):
        if not self.esta_vivo():
            return None
        
        cantidad = random.randint(4, 8) * self.clase.value
        self.cultivos_plantados += 1
        self.ganar_experiencia(7)
        self._actualizar_stats()
        
        for _ in range(cantidad):
            self.agregar_a_inventario(tipo_cultivo)
        
        print(f"🌾 {self.tipo} cultivó {cantidad} {tipo_cultivo}")
        return {'cultivo': tipo_cultivo, 'cantidad': cantidad}
    
    def dar_comida_animales(self, animales, trigo_disponible):
        if not self.esta_vivo():
            return False
        
        trigo_necesario = len(animales)
        if trigo_disponible < trigo_necesario:
            print(f"⚠️ No hay suficiente trigo")
            return False
        
        alimentados = sum(1 for a in animales if hasattr(a, 'comer') and a.comer())
        print(f"🌾 {self.tipo} alimentó {alimentados} animales")
        return True


# ============= GUERRERO (ENANO) =============
class Guerrero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Guerrero', '🛡️', posicion)
        self.fuerza = 5
        self._actualizar_stats()
    
    def _actualizar_stats(self):
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'defensa': 8, 'ataque': 6},
            ClasePersonaje.INTERMEDIO: {'defensa': 12, 'ataque': 10},
            ClasePersonaje.EXPERTO: {'defensa': 16, 'ataque': 14}
        }
        self.defensa = stats[self.clase]['defensa']
        self.ataque = stats[self.clase]['ataque']
    
    def calcular_compatibilidad(self, tipo_accion):
        compatibilidades = {
            'defender': 10,
            'atacar': 10,
            'patrullar': 8,
            'minar': 3,
            'construir': 2
        }
        return compatibilidades.get(tipo_accion, 1) * self.clase.value
    
    def entrenar(self):
        if not self.esta_vivo():
            return False
        self.fuerza += 1 * self.clase.value
        self.ganar_experiencia(5)
        self._actualizar_stats()
        print(f"💪 {self.tipo} entrenó. Fuerza: {self.fuerza}")
        return True
    
    def defender(self, enemigo):
        if not self.esta_vivo():
            return False
        
        poder_guerrero = self.fuerza * self.clase.value
        poder_enemigo = enemigo.poder_ataque
        
        print(f"⚔️ {self.tipo} vs {enemigo.tipo}")
        
        if poder_guerrero >= poder_enemigo:
            enemigo.recibir_dano(poder_guerrero)
            self.ganar_experiencia(20)
            print(f"✅ {self.tipo} defendió exitosamente")
            return True
        else:
            diferencia = poder_enemigo - poder_guerrero
            if diferencia > 30:
                self.morir(f"ataque de {enemigo.tipo}")
            else:
                self.recibir_lesion(f"ataque de {enemigo.tipo}")
            return False


# ============= ENEMIGOS =============
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
        print(f"👹 {self.tipo} ataca a {victima.tipo}")
        if random.random() < 0.3:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        return True
    
    def robar(self, cofre):
        if self.salud <= 0 or not hasattr(cofre, 'recursos_dict'):
            return None
        if not cofre.recursos_dict:
            print(f"👹 {self.tipo} intentó robar pero el cofre está vacío")
            return None
        
        item = random.choice(list(cofre.recursos_dict.keys()))
        cantidad = random.randint(1, min(3, cofre.recursos_dict[item]))
        
        if cofre.retirar(item, cantidad):
            self.objetos_robados.append((item, cantidad))
            print(f"👹 {self.tipo} robó {cantidad} {item}")
            return (item, cantidad)
        return None
    
    def recibir_dano(self, cantidad):
        self.salud -= cantidad
        if self.salud <= 0:
            print(f"💀 {self.tipo} derrotado")


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
        print(f"👺 {self.tipo} ataca a {victima.tipo}")
        if random.random() < 0.5:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        return True
    
    def recibir_dano(self, cantidad):
        self.salud -= cantidad
        if self.salud <= 0:
            print(f"💀 {self.tipo} derrotado")


# ============= ANIMALES =============
class Vaca:
    def __init__(self):
        self.tipo = 'Vaca'
        self.simbolo = '🐄'
        self.hambre = 0
        self.viva = True
        self.leche_disponible = 0
    
    def comer(self):
        if not self.viva:
            return False
        self.hambre = max(0, self.hambre - 50)
        self.leche_disponible += 1
        return True
    
    def dar_leche(self):
        if not self.viva or self.hambre > 50:
            return 0
        leche = self.leche_disponible
        self.leche_disponible = 0
        print(f"🥛 Vaca dio {leche} leches")
        return leche
    
    def sacrificar(self):
        if not self.viva:
            return None
        self.viva = False
        print(f"🔪 Vaca sacrificada")
        return {'carne': 10, 'piel': 5}
    
    def actualizar(self):
        if self.viva:
            self.hambre = min(100, self.hambre + 15)
            if self.hambre >= 100:
                self.viva = False
                print(f"💀 Vaca murió de hambre")


class Gallina:
    def __init__(self):
        self.tipo = 'Gallina'
        self.simbolo = '🐔'
        self.hambre = 0
        self.viva = True
    
    def comer(self):
        if not self.viva:
            return False
        self.hambre = max(0, self.hambre - 50)
        return True
    
    def poner_huevo(self):
        if not self.viva or self.hambre > 50:
            return 0
        huevos = random.randint(1, 3)
        print(f"🥚 Gallina puso {huevos} huevos")
        return huevos
    
    def sacrificar(self):
        if not self.viva:
            return None
        self.viva = False
        print(f"🔪 Gallina sacrificada")
        return {'carne': 2, 'plumas': 5}
    
    def actualizar(self):
        if self.viva:
            self.hambre = min(100, self.hambre + 20)
            if self.hambre >= 100:
                self.viva = False
                print(f"💀 Gallina murió de hambre")


class Cerdo:
    def __init__(self):
        self.tipo = 'Cerdo'
        self.simbolo = '🐷'
        self.hambre = 0
        self.vivo = True
    
    def comer(self):
        if not self.vivo:
            return False
        self.hambre = max(0, self.hambre - 50)
        return True
    
    def sacrificar(self):
        if not self.vivo:
            return None
        self.vivo = False
        print(f"🔪 Cerdo sacrificado")
        return {'carne': 6, 'piel': 2}
    
    def actualizar(self):
        if self.vivo:
            self.hambre = min(100, self.hambre + 18)
            if self.hambre >= 100:
                self.vivo = False
                print(f"💀 Cerdo murió de hambre")


# ============= CULTIVOS =============
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
            print(f"🌾 Trigo maduro para cosechar")
    
    def cosechar(self):
        if not self.maduro:
            print(f"⚠️ Trigo no está maduro")
            return 0
        cantidad = random.randint(5, 10)
        self.maduro = False
        self.crecimiento = 0
        print(f"🌾 Cosechado {cantidad} trigos")
        return cantidad


# ============= COFRE PRINCIPAL (QUEUE) =============
class CofrePrincipal:
    """
    USA QUEUE (FIFO)
    Recursos + herramientas SOLO de la aldea (NO enemigos)
    """
    def __init__(self):
        self.tipo = 'Cofre Principal'
        self.cola_recursos = Queue()
        self.cola_herramientas = Queue()
        self.recursos_dict = {}
        self.herramientas_dict = {}
        self.capacidad = 200
    
    def inicializar_herramientas(self):
        """Herramientas iniciales del juego"""
        herramientas = {
            'pico': 3,
            'hacha': 3,
            'martillo': 2,
            'azada': 2,
            'espada': 2
        }
        for h, cant in herramientas.items():
            self.guardar_herramienta(h, cant)
    
    def guardar(self, recurso, cantidad):
        total = sum(self.recursos_dict.values())
        if total + cantidad > self.capacidad:
            print(f"⚠️ Cofre principal lleno")
            return False
        
        for _ in range(cantidad):
            item = {'tipo': recurso, 'cantidad': 1}
            self.cola_recursos.enqueue(item)
        
        if recurso not in self.recursos_dict:
            self.recursos_dict[recurso] = 0
        self.recursos_dict[recurso] += cantidad
        print(f"📦 Guardado en principal: {cantidad} {recurso}")
        return True
    
    def guardar_herramienta(self, herramienta, cantidad, de_personaje=None):
        """NO acepta items de enemigos"""
        if de_personaje and hasattr(de_personaje, 'tipo'):
            if de_personaje.tipo in ['Duende', 'Orco']:
                print(f"🚫 NO se guardan items de enemigos")
                return False
        
        for _ in range(cantidad):
            item = {'tipo': herramienta, 'cantidad': 1}
            self.cola_herramientas.enqueue(item)
        
        if herramienta not in self.herramientas_dict:
            self.herramientas_dict[herramienta] = 0
        self.herramientas_dict[herramienta] += cantidad
        print(f"🔧 Guardada herramienta: {cantidad} {herramienta}")
        return True
    
    def retirar(self, recurso, cantidad):
        if self.recursos_dict.get(recurso, 0) < cantidad:
            print(f"⚠️ No hay suficiente {recurso}")
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
        
        print(f"📤 Retirado: {cantidad} {recurso}")
        return True
    
    def ver_inventario(self):
        if not self.recursos_dict and not self.herramientas_dict:
            print(f"📦 Cofre principal vacío")
            return
        print(f"📦 COFRE PRINCIPAL:")
        print("  Recursos:")
        for item, cant in self.recursos_dict.items():
            print(f"    {item}: {cant}")
        print("  Herramientas:")
        for item, cant in self.herramientas_dict.items():
            print(f"    {item}: {cant}")


# ============= COFRE ALIMENTOS (DEQUE) =============
class CofreAlimentos:
    """
    USA DEQUE (FIFO por frescura)
    Los alimentos más viejos se toman primero
    """
    def __init__(self):
        self.tipo = 'Cofre Alimentos'
        self.cola_alimentos = Deque()
        self.alimentos_dict = {}
        self.capacidad = 100
    
    def guardar(self, alimento, cantidad):
        items_permitidos = ['carne', 'huevos', 'leche', 'trigo', 'pan', 'plumas', 'piel']
        if alimento not in items_permitidos:
            print(f"⚠️ {alimento} no va en cofre de alimentos")
            return False
        
        total = sum(self.alimentos_dict.values())
        if total + cantidad > self.capacidad:
            print(f"⚠️ Cofre de alimentos lleno")
            return False
        
        for _ in range(cantidad):
            item = {'tipo': alimento, 'frescura': 100}
            self.cola_alimentos.push_back(item)
        
        if alimento not in self.alimentos_dict:
            self.alimentos_dict[alimento] = 0
        self.alimentos_dict[alimento] += cantidad
        print(f"📦 Guardado en alimentos: {cantidad} {alimento}")
        return True
    
    def retirar(self, alimento, cantidad):
        """Retira desde el frente (más viejo primero)"""
        if self.alimentos_dict.get(alimento, 0) < cantidad:
            print(f"⚠️ No hay suficiente {alimento}")
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
        
        print(f"📤 Retirado: {cantidad} {alimento}")
        return True
    
    def actualizar_frescura(self):
        """Degrada frescura, elimina alimentos echados a perder"""
        temp = Deque()
        deteriorados = 0
        
        while not self.cola_alimentos.empty():
            item = self.cola_alimentos.pop_front()
            item['frescura'] -= 10
            
            if item['frescura'] <= 0:
                deteriorados += 1
                self.alimentos_dict[item['tipo']] -= 1
                if self.alimentos_dict[item['tipo']] == 0:
                    del self.alimentos_dict[item['tipo']]
            else:
                temp.push_back(item)
        
        while not temp.empty():
            self.cola_alimentos.push_back(temp.pop_front())
        
        if deteriorados > 0:
            print(f"🦠 {deteriorados} alimentos se echaron a perder")
    
    def ver_inventario(self):
        if not self.alimentos_dict:
            print(f"📦 Cofre de alimentos vacío")
            return
        print(f"📦 COFRE ALIMENTOS:")
        for item, cant in self.alimentos_dict.items():
            print(f"   {item}: {cant}")


# ============= CLIMA =============
class Lluvia:
    def __init__(self):
        self.tipo = 'Lluvia'
        self.simbolo = '🌧️'
        self.activa = False
    
    def activar(self):
        self.activa = True
        print(f"🌧️ ¡Comenzó a llover!")
    
    def aplicar_efectos(self, cultivos):
        if not self.activa:
            return
        print(f"🌧️ La lluvia hace crecer los cultivos...")
        for cultivo in cultivos:
            cultivo.crecer(hay_lluvia=True)
    
    def detener(self):
        self.activa = False
        print(f"☀️ La lluvia terminó")


class Tormenta:
    def __init__(self):
        self.tipo = 'Tormenta'
        self.simbolo = '⛈️'
        self.activa = False
        self.intensidad = 0
    
    def activar(self, intensidad=5):
        self.activa = True
        self.intensidad = intensidad
        print(f"⛈️ ¡Tormenta! (Intensidad: {intensidad})")
    
    def aplicar_efectos(self, personajes):
        if not self.activa:
            return
        
        prob_rayo = self.intensidad * 0.1
        if random.random() < prob_rayo and personajes:
            victima = random.choice(personajes)
            if victima.esta_vivo():
                print(f"⚡ ¡Rayo!")
                victima.morir("impacto de rayo")
        
        prob_inundacion = self.intensidad * 0.08
        if random.random() < prob_inundacion and personajes:
            afectados = random.sample(personajes, min(len(personajes), 3))
            print(f"🌊 ¡Inundación!")
            for personaje in afectados:
                if personaje.esta_vivo():
                    personaje.recibir_lesion("inundación")
    
    def detener(self):
        self.activa = False
        print(f"☀️ La tormenta pasó")


class Tornado:
    def __init__(self):
        self.tipo = 'Tornado'
        self.simbolo = '🌪️'
        self.activo = False
    
    def activar(self):
        self.activo = True
        print(f"🌪️ ¡TORNADO! ¡Peligro extremo!")
    
    def aplicar_efectos(self, personajes, animales, estructuras):
        if not self.activo:
            return
        
        print(f"🌪️ El tornado causa destrucción masiva...")
        
        animales_muertos = 0
        for animal in animales:
            if hasattr(animal, 'viva'):
                if animal.viva and random.random() < 0.6:
                    animal.viva = False
                    animales_muertos += 1
            elif hasattr(animal, 'vivo'):
                if animal.vivo and random.random() < 0.6:
                    animal.vivo = False
                    animales_muertos += 1
        print(f"   💀 {animales_muertos} animales murieron")
        
        estructuras_destruidas = 0
        for estructura in estructuras:
            if random.random() < 0.7:
                estructura['destruida'] = True
                estructuras_destruidas += 1
        print(f"   🏚️ {estructuras_destruidas} estructuras destruidas")
        
        personajes_muertos = 0
        for personaje in personajes:
            if personaje.esta_vivo() and random.random() < 0.4:
                personaje.morir("tornado")
                personajes_muertos += 1
        print(f"   💀 {personajes_muertos} personajes murieron")
    
    def detener(self):
        self.activo = False
        print(f"☀️ El tornado se disipó")
