

import random
from enum import Enum


try:
   
    from ListaEnlazada import LinkedList, to_list, length, find
    TIENE_LISTA = True
except ImportError:
    TIENE_LISTA = False

try:
    from deque import Deque
    TIENE_DEQUE = True
except ImportError:
    TIENE_DEQUE = False


# =============================================================================
# ENUMERACIONES
# =============================================================================

class ClasePersonaje(Enum):
    """Niveles de experiencia de personajes"""
    PRINCIPIANTE = 1
    INTERMEDIO = 2
    EXPERTO = 3


class EstadoPersonaje(Enum):
    """Estados posibles de un personaje"""
    VIVO = "vivo"
    LESIONADO = "lesionado"
    MUERTO = "muerto"


# =============================================================================
# CLASE BASE ABSTRACTA
# =============================================================================

class Personaje:

    
    def __init__(self, tipo: str, simbolo: str, posicion: tuple = (0, 0)):
        self.tipo = tipo
        self.simbolo = simbolo
        self.posicion = posicion
        self.clase = ClasePersonaje.PRINCIPIANTE
        self.experiencia = 0
        self.estado = EstadoPersonaje.VIVO
        self.salud = 100
        
        if TIENE_LISTA:
            self.inventario = LinkedList()
        else:
            self.inventario = {}  # Fallback
    
    def ganar_experiencia(self, puntos: int):
    
        self.experiencia += puntos
        
        if self.experiencia >= 100 and self.clase == ClasePersonaje.PRINCIPIANTE:
            self.clase = ClasePersonaje.INTERMEDIO
            self.experiencia = 0
            print(f"⬆️ {self.tipo} subió a INTERMEDIO")
        
        elif self.experiencia >= 200 and self.clase == ClasePersonaje.INTERMEDIO:
            self.clase = ClasePersonaje.EXPERTO
            self.experiencia = 0
            print(f"⬆️ {self.tipo} subió a EXPERTO")
    
    def recibir_lesion(self, descripcion: str, es_mortal: bool = False):
        """
        Recibe una lesión.
        
        """
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
                print(f"🩹 {self.tipo} lesionado por {descripcion} (Salud: {self.salud})")
    
    def morir(self, causa: str):
        """Marca al personaje como muerto"""
        self.estado = EstadoPersonaje.MUERTO
        self.salud = 0
        print(f"💀 {self.tipo} murió por {causa}")
    
    def esta_vivo(self) -> bool:
        """Verifica si el personaje está vivo"""
        return self.estado != EstadoPersonaje.MUERTO
    
    def comer(self) -> bool:
        """
        Acción de comer - restaura salud.
        
        """
        if not self.esta_vivo():
            return False
        
        self.salud = min(100, self.salud + 20)
        print(f"🍖 {self.tipo} comió (Salud: {self.salud})")
        return True
    
    def agregar_a_inventario(self, item: str):
        """
        Agrega item al inventario (usa estructura propia).
        
        """
        if TIENE_LISTA:
            self.inventario.add(item)
        else:
            if item not in self.inventario:
                self.inventario[item] = 0
            self.inventario[item] += 1
    
    def tiene_en_inventario(self, item: str) -> bool:
        """
        Verifica si tiene un item en el inventario.
        
        Args:
            item (str): Item a buscar
        
        Returns:
            bool: True si lo tiene
        """
        if TIENE_LISTA:
            resultados = find(self.inventario, lambda x: x == item)
            return len(resultados) > 0
        else:
            return item in self.inventario and self.inventario[item] > 0
    
    def obtener_inventario(self) -> list:
        """
        Obtiene contenido del inventario.
        
        Returns:
            list: Lista de items en inventario
        """
        if TIENE_LISTA:
            return to_list(self.inventario)
        else:
            return list(self.inventario.keys())
    
    def __repr__(self):
        return f"{self.simbolo} {self.tipo} ({self.clase.name})"


# =============================================================================
# TRABAJADORES (5 tipos, cada uno con 3 niveles)
# =============================================================================

class Minero(Personaje):
    """
    """
    
    def __init__(self, posicion: tuple = (0, 0)):
        super().__init__('Minero', '⛏️', posicion)
        self.materiales_minados = 0
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas según la clase"""
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'minar': 10, 'velocidad': 1.0},
            ClasePersonaje.INTERMEDIO: {'minar': 15, 'velocidad': 1.5},
            ClasePersonaje.EXPERTO: {'minar': 20, 'velocidad': 2.0}
        }
        self.habilidad_minar = stats[self.clase]['minar']
        self.velocidad = stats[self.clase]['velocidad']
    
    def minar(self) -> dict:
        """
        Acción de minar - extrae piedra.
        
        Returns:
            dict: {'recurso': 'piedra', 'cantidad': int} o None si murió
        """
        if not self.esta_vivo():
            return None
        
        # Verificar muerte por asfixia (5%)
        if random.random() < 0.05:
            self.morir("asfixia en la mina")
            return None
        
        # Verificar muerte por intoxicación (3%)
        if random.random() < 0.03:
            self.morir("intoxicación por gases")
            return None
        
        # Minar exitosamente
        cantidad = random.randint(2, 5) * int(self.habilidad_minar * self.velocidad / 10)
        self.materiales_minados += cantidad
        self.ganar_experiencia(10)
        self._actualizar_estadisticas()
        
        # Agregar a inventario
        for _ in range(cantidad):
            self.agregar_a_inventario('piedra')
        
        print(f"⛏️ {self.tipo} ({self.clase.name}) minó {cantidad} piedras")
        return {'recurso': 'piedra', 'cantidad': cantidad}


class Enano(Personaje):
    """
    
    """
    
    def __init__(self, posicion: tuple = (0, 0)):
        super().__init__('Enano', '🛡️', posicion)
        self.fuerza = 5
        self.cerveza_producida = 0
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas según la clase"""
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'defensa': 8, 'ataque': 6},
            ClasePersonaje.INTERMEDIO: {'defensa': 12, 'ataque': 10},
            ClasePersonaje.EXPERTO: {'defensa': 16, 'ataque': 14}
        }
        self.defensa = stats[self.clase]['defensa']
        self.ataque = stats[self.clase]['ataque']
    
    def entrenar(self) -> bool:
        """
        Entrena para mejorar fuerza.
        
        Returns:
            bool: True si entrenó exitosamente
        """
        if not self.esta_vivo():
            return False
        
        incremento = 1 * self.clase.value
        self.fuerza += incremento
        self.ganar_experiencia(5)
        self._actualizar_estadisticas()
        
        print(f"💪 {self.tipo} ({self.clase.name}) entrenó. Fuerza: {self.fuerza}")
        return True
    
    def defender(self, enemigo) -> bool:
      
        if not self.esta_vivo():
            return False
        
        poder_enano = self.fuerza * self.clase.value
        poder_enemigo = enemigo.poder_ataque
        
        print(f"⚔️ {self.tipo} (Fuerza: {poder_enano}) vs {enemigo.tipo} (Ataque: {poder_enemigo})")
        
        if poder_enano >= poder_enemigo:
            # Victoria
            enemigo.recibir_dano(poder_enano)
            self.ganar_experiencia(20)
            self._actualizar_estadisticas()
            print(f"✅ {self.tipo} defendió exitosamente")
            return True
        else:
            # Derrota
            diferencia = poder_enemigo - poder_enano
            if diferencia > 30:
                self.morir(f"ataque de {enemigo.tipo}")
            else:
                self.recibir_lesion(f"ataque de {enemigo.tipo}")
            return False
    
    def hacer_cerveza(self, cebada_cantidad: int) -> int:
      
        if not self.esta_vivo() or cebada_cantidad < 2:
            return 0
        
        cerveza = (cebada_cantidad // 2) * self.clase.value
        self.cerveza_producida += cerveza
        
        print(f"🍺 {self.tipo} ({self.clase.name}) produjo {cerveza} cervezas")
        return cerveza


class Lenador(Personaje):

    
    def __init__(self, posicion: tuple = (0, 0)):
        super().__init__('Leñador', '🪓', posicion)
        self.arboles_talados = 0
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas según la clase"""
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'talar': 10, 'velocidad': 1.0},
            ClasePersonaje.INTERMEDIO: {'talar': 15, 'velocidad': 1.5},
            ClasePersonaje.EXPERTO: {'talar': 20, 'velocidad': 2.0}
        }
        self.habilidad_talar = stats[self.clase]['talar']
        self.velocidad = stats[self.clase]['velocidad']
    
    def talar(self) -> dict:
       
        if not self.esta_vivo():
            return None
        
        # Verificar muerte por árbol caído (7%)
        if random.random() < 0.07:
            self.morir("árbol caído encima")
            return None
        
        # Verificar lesión por hacha (10%)
        if random.random() < 0.10:
            self.recibir_lesion("corte con hacha")
        
        # Talar exitosamente
        cantidad = random.randint(3, 6) * int(self.habilidad_talar * self.velocidad / 10)
        self.arboles_talados += 1
        self.ganar_experiencia(8)
        self._actualizar_estadisticas()
        
        # Agregar a inventario
        for _ in range(cantidad):
            self.agregar_a_inventario('madera')
        
        print(f"🪓 {self.tipo} ({self.clase.name}) taló {cantidad} maderas")
        return {'recurso': 'madera', 'cantidad': cantidad}


class Constructor(Personaje):
    """
    Constructor - Experto en construir.
    
    Niveles:
        - Principiante: construir=10, precisión=0.7
        - Intermedio: construir=15, precisión=0.85
        - Experto: construir=20, precisión=0.95
    
    Lesiones posibles:
        - Lesión por golpe con martillo (probabilidad según precisión)
        - Muerte por ataque de duende/orco
    
    Acciones:
        - construir(tipo_estructura): Construye edificios
        - comer(): Restaura salud
    """
    
    def __init__(self, posicion: tuple = (0, 0)):
        super().__init__('Constructor', '🔨', posicion)
        self.estructuras_construidas = 0
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas según la clase"""
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'construir': 10, 'precision': 0.7},
            ClasePersonaje.INTERMEDIO: {'construir': 15, 'precision': 0.85},
            ClasePersonaje.EXPERTO: {'construir': 20, 'precision': 0.95}
        }
        self.habilidad_construir = stats[self.clase]['construir']
        self.precision = stats[self.clase]['precision']
    
    def construir(self, tipo_estructura: str = 'edificio') -> dict:
      
        if not self.esta_vivo():
            return None
        
        # Verificar lesión por martillo (menor probabilidad si es experto)
        if random.random() < (1 - self.precision) * 0.3:
            self.recibir_lesion("golpe con martillo")
        
        # Construir exitosamente
        tiempo_construccion = max(1, 10 - (self.clase.value * 2))
        self.estructuras_construidas += 1
        self.ganar_experiencia(15)
        self._actualizar_estadisticas()
        
        print(f"🔨 {self.tipo} ({self.clase.name}) construyó {tipo_estructura} (tiempo: {tiempo_construccion})")
        return {'estructura': tipo_estructura, 'tiempo': tiempo_construccion}


class Granjero(Personaje):
    """
    Granjero - Experto en agricultura.
    
    Niveles:
        - Principiante: cultivar=8, cuidado_animal=6
        - Intermedio: cultivar=12, cuidado_animal=10
        - Experto: cultivar=16, cuidado_animal=14
    
    Lesiones posibles:
        - Lesión por ataque de vaca (5% probabilidad)
        - Muerte por ataque de duende/orco
    
    Acciones:
        - cultivar(tipo_cultivo): Planta trigo o cebada
        - dar_comida_animales(animales, trigo): Alimenta animales
        - comer(): Restaura salud
    """
    
    def __init__(self, posicion: tuple = (0, 0)):
        super().__init__('Granjero', '👨‍🌾', posicion)
        self.cultivos_plantados = 0
        self._actualizar_estadisticas()
    
    def _actualizar_estadisticas(self):
        """Actualiza estadísticas según la clase"""
        stats = {
            ClasePersonaje.PRINCIPIANTE: {'cultivar': 8, 'cuidado_animal': 6},
            ClasePersonaje.INTERMEDIO: {'cultivar': 12, 'cuidado_animal': 10},
            ClasePersonaje.EXPERTO: {'cultivar': 16, 'cuidado_animal': 14}
        }
        self.habilidad_cultivar = stats[self.clase]['cultivar']
        self.cuidado_animal = stats[self.clase]['cuidado_animal']
    
    def cultivar(self, tipo_cultivo: str = 'trigo') -> dict:
        """
        Acción de cultivar plantas.
        
        Args:
            tipo_cultivo (str): 'trigo' o 'cebada'
        
        Returns:
            dict: {'cultivo': str, 'cantidad': int}
        """
        if not self.esta_vivo():
            return None
        
        cantidad = random.randint(4, 8) * self.clase.value
        self.cultivos_plantados += 1
        self.ganar_experiencia(7)
        self._actualizar_estadisticas()
        
        # Agregar a inventario
        for _ in range(cantidad):
            self.agregar_a_inventario(tipo_cultivo)
        
        print(f"🌾 {self.tipo} ({self.clase.name}) cultivó {cantidad} {tipo_cultivo}")
        return {'cultivo': tipo_cultivo, 'cantidad': cantidad}
    
    def dar_comida_animales(self, animales: list, trigo_disponible: int) -> bool:
        """
        Alimenta a los animales.
        
        Args:
            animales (list): Lista de animales
            trigo_disponible (int): Cantidad de trigo disponible
        
        Returns:
            bool: True si alimentó exitosamente
        """
        if not self.esta_vivo():
            return False
        
        trigo_necesario = len(animales)
        if trigo_disponible < trigo_necesario:
            print(f"⚠️ No hay suficiente trigo. Necesario: {trigo_necesario}, Disponible: {trigo_disponible}")
            return False
        
        animales_alimentados = 0
        for animal in animales:
            if hasattr(animal, 'comer') and animal.comer():
                animales_alimentados += 1
        
        print(f"🌾 {self.tipo} alimentó {animales_alimentados} animales")
        return True


# =============================================================================
# ENEMIGOS
# =============================================================================

class Duende:
    """
    Duende - Enemigo.
    
    Atributos:
        poder_ataque (int): 20-35
        salud (int): 50
    
    Acciones:
        - atacar(victima): Ataca a un personaje (30% probabilidad de matar)
        - robar(cofre): Roba items de un cofre
    """
    
    def __init__(self, posicion: tuple = (0, 0)):
        self.tipo = 'Duende'
        self.simbolo = '👹'
        self.posicion = posicion
        self.poder_ataque = random.randint(20, 35)
        self.salud = 50
        self.objetos_robados = []
    
    def atacar(self, victima: Personaje) -> bool:
        
        if self.salud <= 0:
            return False
        
        print(f"👹 {self.tipo} ataca a {victima.tipo}")
        
        # 30% probabilidad de matar directamente
        if random.random() < 0.3:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        
        return True
    
    def robar(self, cofre) -> tuple:
      
        if self.salud <= 0 or not hasattr(cofre, 'contenido'):
            return None
        
        if not cofre.contenido:
            print(f"👹 {self.tipo} intentó robar pero el cofre está vacío")
            return None
        
        # Robar item aleatorio
        item_robado = random.choice(list(cofre.contenido.keys()))
        cantidad_maxima = cofre.contenido[item_robado]
        cantidad_robada = random.randint(1, min(3, cantidad_maxima))
        
        if cofre.retirar(item_robado, cantidad_robada):
            self.objetos_robados.append((item_robado, cantidad_robada))
            print(f"👹 {self.tipo} robó {cantidad_robada} {item_robado}")
            return (item_robado, cantidad_robada)
        
        return None
    
    def recibir_dano(self, cantidad: int):
        """Recibe daño de un defensor"""
        self.salud -= cantidad
        if self.salud <= 0:
            print(f"💀 {self.tipo} fue derrotado")
    
    def __repr__(self):
        return f"{self.simbolo} {self.tipo} (Ataque: {self.poder_ataque})"


class Orco:
    """
    Orco - Enemigo fuerte.
    
    Atributos:
        poder_ataque (int): 35-50
        salud (int): 80
    
    Acciones:
        - atacar(victima): Ataca ferozmente (50% probabilidad de matar)
    """
    
    def __init__(self, posicion: tuple = (0, 0)):
        self.tipo = 'Orco'
        self.simbolo = '👺'
        self.posicion = posicion
        self.poder_ataque = random.randint(35, 50)
        self.salud = 80
    
    def atacar(self, victima: Personaje) -> bool:
      
        if self.salud <= 0:
            return False
        
        print(f"👺 {self.tipo} ataca ferozmente a {victima.tipo}")
        
        # 50% probabilidad de matar
        if random.random() < 0.5:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        
        return True
    
    def recibir_dano(self, cantidad: int):
        """Recibe daño de un defensor"""
        self.salud -= cantidad
        if self.salud <= 0:
            print(f"💀 {self.tipo} fue derrotado")
    
    def __repr__(self):
        return f"{self.simbolo} {self.tipo} (Ataque: {self.poder_ataque})"


# =============================================================================
# ANIMALES
# =============================================================================

class Vaca:
    """
    Vaca - Animal que produce leche.
    
    Atributos:
        hambre (int): Nivel de hambre (0-100)
        viva (bool): Estado de vida
        leche_disponible (int): Leche acumulada
    
    Acciones:
        - comer(): Come y produce leche
        - dar_leche(): Retorna leche disponible
        - sacrificar(): Obtiene carne y piel
        - atacar_personaje(personaje): 5% probabilidad de atacar
    """
    
    def __init__(self):
        self.tipo = 'Vaca'
        self.simbolo = '🐄'
        self.hambre = 0
        self.viva = True
        self.leche_disponible = 0
    
    def comer(self) -> bool:
        """Come y reduce hambre"""
        if not self.viva:
            return False
        
        self.hambre = max(0, self.hambre - 50)
        self.leche_disponible += 1
        return True
    
    def dar_leche(self) -> int:
        """Retorna leche disponible"""
        if not self.viva or self.hambre > 50:
            return 0
        
        leche = self.leche_disponible
        self.leche_disponible = 0
        print(f"🥛 Vaca dio {leche} leches")
        return leche
    
    def sacrificar(self) -> dict:
        """Sacrifica la vaca"""
        if not self.viva:
            return None
        
        self.viva = False
        print(f"🔪 Vaca sacrificada")
        return {'carne': 10, 'piel': 5, 'leche': self.leche_disponible}
    
    def atacar_personaje(self, personaje: Personaje) -> bool:
        """Ataca a un personaje (5% probabilidad)"""
        if not self.viva:
            return False
        
        if random.random() < 0.05:
            personaje.recibir_lesion("ataque de vaca")
            print(f"🐄 ¡Vaca atacó a {personaje.tipo}!")
            return True
        
        return False
    
    def actualizar(self):
        """Actualiza estado - aumenta hambre"""
        if self.viva:
            self.hambre = min(100, self.hambre + 15)
            if self.hambre >= 100:
                self.viva = False
                print(f"💀 Vaca murió de hambre")


class Gallina:
    """
    Gallina - Animal que pone huevos.
    
    Atributos:
        hambre (int): Nivel de hambre (0-100)
        viva (bool): Estado de vida
    
    Acciones:
        - comer(): Come y reduce hambre
        - poner_huevo(): Produce huevos (1-3)
        - sacrificar(): Obtiene carne y plumas
    """
    
    def __init__(self):
        self.tipo = 'Gallina'
        self.simbolo = '🐔'
        self.hambre = 0
        self.viva = True
    
    def comer(self) -> bool:
        """Come y reduce hambre"""
        if not self.viva:
            return False
        
        self.hambre = max(0, self.hambre - 50)
        return True
    
    def poner_huevo(self) -> int:
        """Pone huevos si está bien alimentada"""
        if not self.viva or self.hambre > 50:
            return 0
        
        huevos = random.randint(1, 3)
        print(f"🥚 Gallina puso {huevos} huevos")
        return huevos
    
    def sacrificar(self) -> dict:
        """Sacrifica la gallina"""
        if not self.viva:
            return None
        
        self.viva = False
        print(f"🔪 Gallina sacrificada")
        return {'carne': 2, 'plumas': 5}
    
    def actualizar(self):
        """Actualiza estado - aumenta hambre"""
        if self.viva:
            self.hambre = min(100, self.hambre + 20)
            if self.hambre >= 100:
                self.viva = False
                print(f"💀 Gallina murió de hambre")


class Cerdo:
    """
    Cerdo - Animal para carne.
    
    Atributos:
        hambre (int): Nivel de hambre (0-100)
        vivo (bool): Estado de vida
    
    Acciones:
        - comer(): Come y reduce hambre
        - sacrificar(): Obtiene carne y piel
    """
    
    def __init__(self):
        self.tipo = 'Cerdo'
        self.simbolo = '🐷'
        self.hambre = 0
        self.vivo = True
    
    def comer(self) -> bool:
        """Come y reduce hambre"""
        if not self.vivo:
            return False
        
        self.hambre = max(0, self.hambre - 50)
        return True
    
    def sacrificar(self) -> dict:
        """Sacrifica el cerdo"""
        if not self.vivo:
            return None
        
        self.vivo = False
        print(f"🔪 Cerdo sacrificado")
        return {'carne': 6, 'piel': 2}
    
    def actualizar(self):
        """Actualiza estado - aumenta hambre"""
        if self.vivo:
            self.hambre = min(100, self.hambre + 18)
            if self.hambre >= 100:
                self.vivo = False
                print(f"💀 Cerdo murió de hambre")


# =============================================================================
# CULTIVOS
# =============================================================================

class Trigo:
    """
    Trigo - Cultivo para alimentar animales o hacer pan.
    
    Atributos:
        crecimiento (int): Nivel de crecimiento (0-100)
        maduro (bool): Si está listo para cosechar
        uso (str): Usos del trigo
    
    Acciones:
        - crecer(hay_lluvia): Crece (30 con lluvia, 15 sin lluvia)
        - cosechar(): Retorna 5-10 trigos
    """
    
    def __init__(self):
        self.tipo = 'trigo'
        self.crecimiento = 0
        self.maduro = False
        self.uso = 'alimentar animales o hacer pan'
    
    def crecer(self, hay_lluvia: bool = False):
        """Crece más rápido con lluvia"""
        if self.maduro:
            return
        
        incremento = 30 if hay_lluvia else 15
        self.crecimiento = min(100, self.crecimiento + incremento)
        
        if self.crecimiento >= 100:
            self.maduro = True
            print(f"🌾 Trigo está maduro para cosechar")
    
    def cosechar(self) -> int:
        """Cosecha el trigo maduro"""
        if not self.maduro:
            print(f"⚠️ Trigo no está maduro")
            return 0
        
        cantidad = random.randint(5, 10)
        self.maduro = False
        self.crecimiento = 0
        print(f"🌾 Cosechado {cantidad} trigos")
        return cantidad


class Cebada:
    """
    Cebada - Cultivo para hacer cerveza.
    
    Atributos:
        crecimiento (int): Nivel de crecimiento (0-100)
        maduro (bool): Si está listo para cosechar
        uso (str): Usos de la cebada
    
    Acciones:
        - crecer(hay_lluvia): Crece (30 con lluvia, 15 sin lluvia)
        - cosechar(): Retorna 4-9 cebadas
    """
    
    def __init__(self):
        self.tipo = 'cebada'
        self.crecimiento = 0
        self.maduro = False
        self.uso = 'hacer cerveza'
    
    def crecer(self, hay_lluvia: bool = False):
        """Crece más rápido con lluvia"""
        if self.maduro:
            return
        
        incremento = 30 if hay_lluvia else 15
        self.crecimiento = min(100, self.crecimiento + incremento)
        
        if self.crecimiento >= 100:
            self.maduro = True
            print(f"🌾 Cebada está madura para cosechar")
    
    def cosechar(self) -> int:
        """Cosecha la cebada madura"""
        if not self.maduro:
            print(f"⚠️ Cebada no está madura")
            return 0
        
        cantidad = random.randint(4, 9)
        self.maduro = False
        self.crecimiento = 0
        print(f"🌾 Cosechado {cantidad} cebadas")
        return cantidad


# =============================================================================
# COFRES (Sistema de almacenamiento)
# =============================================================================

class CofreComida:
    """
    Cofre para guardar comida de animales y cultivos.
    
    Atributos:
        contenido (dict): Items almacenados {item: cantidad}
        capacidad (int): Capacidad máxima (100)
    
    Acciones:
        - guardar(item, cantidad): Almacena items permitidos
        - retirar(item, cantidad): Retira items
        - ver_inventario(): Muestra contenido
    
    Items permitidos:
        carne, huevos, leche, trigo, cebada, pan, plumas, piel
    """
    
    def __init__(self):
        self.tipo = 'Cofre de Comida y Cultivos'
        self.contenido = {}
        self.capacidad = 100
    
    def guardar(self, item: str, cantidad: int) -> bool:
        """Guarda comida de animales o cultivos"""
        items_permitidos = ['carne', 'huevos', 'leche', 'trigo', 'cebada', 
                           'pan', 'plumas', 'piel']
        
        if item not in items_permitidos:
            print(f"⚠️ {item} no se puede guardar en el cofre de comida")
            return False
        
        total_actual = sum(self.contenido.values())
        if total_actual + cantidad > self.capacidad:
            print(f"⚠️ Cofre lleno. Capacidad: {self.capacidad}")
            return False
        
        if item not in self.contenido:
            self.contenido[item] = 0
        
        self.contenido[item] += cantidad
        print(f"📦 Guardado {cantidad} {item} en cofre de comida")
        return True
    
    def retirar(self, item: str, cantidad: int) -> bool:
        """Retira items del cofre"""
        if item not in self.contenido or self.contenido[item] < cantidad:
            print(f"⚠️ No hay suficiente {item} en el cofre")
            return False
        
        self.contenido[item] -= cantidad
        if self.contenido[item] == 0:
            del self.contenido[item]
        
        print(f"📤 Retirado {cantidad} {item} del cofre de comida")
        return True
    
    def ver_inventario(self):
        """Muestra el inventario del cofre"""
        if not self.contenido:
            print(f"📦 Cofre de comida vacío")
            return
        
        print(f"📦 Contenido del cofre de comida:")
        for item, cantidad in self.contenido.items():
            print(f"   {item}: {cantidad}")


class CofreInicial:
    """
    Cofre inicial para guardar cualquier tipo de recurso.
    
    Atributos:
        contenido (dict): Items almacenados {item: cantidad}
        capacidad (int): Capacidad máxima (150)
    
    Acciones:
        - guardar(item, cantidad): Almacena cualquier recurso
        - retirar(item, cantidad): Retira items
        - ver_inventario(): Muestra contenido
    """
    
    def __init__(self):
        self.tipo = 'Cofre Inicial'
        self.contenido = {}
        self.capacidad = 150
    
    def guardar(self, item: str, cantidad: int) -> bool:
        """Guarda cualquier tipo de recurso"""
        total_actual = sum(self.contenido.values())
        if total_actual + cantidad > self.capacidad:
            print(f"⚠️ Cofre lleno. Capacidad: {self.capacidad}")
            return False
        
        if item not in self.contenido:
            self.contenido[item] = 0
        
        self.contenido[item] += cantidad
        print(f"📦 Guardado {cantidad} {item} en cofre inicial")
        return True
    
    def retirar(self, item: str, cantidad: int) -> bool:
        """Retira items del cofre"""
        if item not in self.contenido or self.contenido[item] < cantidad:
            print(f"⚠️ No hay suficiente {item} en el cofre")
            return False
        
        self.contenido[item] -= cantidad
        if self.contenido[item] == 0:
            del self.contenido[item]
        
        print(f"📤 Retirado {cantidad} {item} del cofre inicial")
        return True
    
    def ver_inventario(self):
        """Muestra el inventario del cofre"""
        if not self.contenido:
            print(f"📦 Cofre inicial vacío")
            return
        
        print(f"📦 Contenido del cofre inicial:")
        for item, cantidad in self.contenido.items():
            print(f"   {item}: {cantidad}")


# =============================================================================
# CLIMA (Eventos que afectan el juego)
# =============================================================================


class Lluvia:
    
    def __init__(self):
        self.tipo = 'Lluvia'
        self.simbolo = '🌧️'
        self.activa = False
    
    def activar(self):
        """Activa la lluvia"""
        self.activa = True
        print(f"🌧️ ¡Comenzó a llover!")
    
    def aplicar_efectos(self, cultivos: list):
        """Hace crecer los cultivos más rápido"""
        if not self.activa:
            return
        
        print(f"🌧️ La lluvia hace crecer los cultivos...")
        for cultivo in cultivos:
            if hasattr(cultivo, 'crecer'):
                cultivo.crecer(hay_lluvia=True)
    
    def detener(self):
        """Detiene la lluvia"""
        self.activa = False
        print(f"☀️ La lluvia terminó")


class Tormenta:
    """
    Tormenta - Puede caer rayos o causar inundaciones.
    
    Efectos:
        - Rayos: Matan personajes (probabilidad según intensidad)
        - Inundaciones: Lesionan a varios personajes
    """
    
    def __init__(self):
        self.tipo = 'Tormenta'
        self.simbolo = '⛈️'
        self.activa = False
        self.intensidad = 0
    
    def activar(self, intensidad: int = 5):
        """Activa la tormenta"""
        self.activa = True
        self.intensidad = intensidad
        print(f"⛈️ ¡Comenzó una tormenta! (Intensidad: {intensidad})")
    
    def aplicar_efectos(self, personajes: list):
        """Puede caer rayos o causar inundaciones"""
        if not self.activa or not personajes:
            return
        
        personajes_vivos = [p for p in personajes if hasattr(p, 'esta_vivo') and p.esta_vivo()]
        
        if not personajes_vivos:
            return
        
        # Rayos (probabilidad según intensidad)
        prob_rayo = self.intensidad * 0.1
        if random.random() < prob_rayo:
            victima = random.choice(personajes_vivos)
            print(f"⚡ ¡Un rayo cayó!")
            victima.morir("impacto de rayo")
        
        # Inundaciones (probabilidad según intensidad)
        prob_inundacion = self.intensidad * 0.08
        if random.random() < prob_inundacion:
            cantidad_afectados = min(len(personajes_vivos), 3)
            afectados = random.sample(personajes_vivos, cantidad_afectados)
            print(f"🌊 ¡Inundación!")
            for personaje in afectados:
                personaje.recibir_lesion("inundación")
    
    def detener(self):
        """Detiene la tormenta"""
        self.activa = False
        print(f"☀️ La tormenta pasó")


class Tornado:
    """
    Tornado - Destrucción masiva.
    
    Efectos:
        - Mata animales (60% probabilidad)
        - Destruye estructuras (70% probabilidad)
        - Mata personajes (40% probabilidad)
    """
    
    def __init__(self):
        self.tipo = 'Tornado'
        self.simbolo = '🌪️'
        self.activo = False
    
    def activar(self):
        """Activa el tornado"""
        self.activo = True
        print(f"🌪️ ¡TORNADO! ¡Peligro extremo!")
    
    def aplicar_efectos(self, personajes: list, animales: list, estructuras: list):
        """Destrucción masiva: mata animales, destruye estructuras, mata personajes"""
        if not self.activo:
            return
        
        print(f"🌪️ El tornado causa destrucción masiva...")
        
        # Matar animales (60% probabilidad)
        animales_muertos = 0
        for animal in animales:
            if hasattr(animal, 'viva') and animal.viva:
                if random.random() < 0.6:
                    animal.viva = False
                    animales_muertos += 1
            elif hasattr(animal, 'vivo') and animal.vivo:
                if random.random() < 0.6:
                    animal.vivo = False
                    animales_muertos += 1
        
        print(f"   💀 {animales_muertos} animales murieron")
        
        # Destruir estructuras (70% probabilidad)
        estructuras_destruidas = 0
        for estructura in estructuras:
            if random.random() < 0.7:
                estructura['destruida'] = True
                estructuras_destruidas += 1
        
        print(f"   🏚️ {estructuras_destruidas} estructuras destruidas")
        
        # Matar personajes (40% probabilidad)
        personajes_muertos = 0
        for personaje in personajes:
            if hasattr(personaje, 'esta_vivo') and personaje.esta_vivo():
                if random.random() < 0.4:
                    personaje.morir("tornado")
                    personajes_muertos += 1
        
        print(f"   💀 {personajes_muertos} personajes murieron")
    
    def detener(self):
        """Detiene el tornado"""
        self.activo = False
        print(f"☀️ El tornado se disipó")
