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
        self.experiencia = 0
        self.estado = EstadoPersonaje.VIVO
        self.salud = 100
        self.inventario = {}
        
    def ganar_experiencia(self, puntos):
        """Sube de clase según la experiencia"""
        self.experiencia += puntos
        if self.experiencia >= 100 and self.clase == ClasePersonaje.PRINCIPIANTE:
            self.clase = ClasePersonaje.INTERMEDIO
            self.experiencia = 0
            print(f"⬆️ {self.tipo} subió a INTERMEDIO")
        elif self.experiencia >= 200 and self.clase == ClasePersonaje.INTERMEDIO:
            self.clase = ClasePersonaje.EXPERTO
            self.experiencia = 0
            print(f"⬆️ {self.tipo} subió a EXPERTO")
    
    def recibir_lesion(self, descripcion, es_mortal=False):
        """Recibe una lesión"""
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
    
    def morir(self, causa):
        """Marca al personaje como muerto"""
        self.estado = EstadoPersonaje.MUERTO
        self.salud = 0
        print(f"💀 {self.tipo} murió por {causa}")
    
    def esta_vivo(self):
        return self.estado != EstadoPersonaje.MUERTO
    
    def comer(self):
        """Acción de comer - restaura salud"""
        if not self.esta_vivo():
            return False
        self.salud = min(100, self.salud + 20)
        print(f"🍖 {self.tipo} comió (Salud: {self.salud})")
        return True

# ============= MINERO =============
class Minero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Minero', '⛏️', posicion)
        self.materiales_minados = 0
        
    def minar(self):
        """Acción de minar - puede morir por asfixia o intoxicación"""
        if not self.esta_vivo():
            return None
        
        # Verificar muerte por asfixia (5% de probabilidad)
        if random.random() < 0.05:
            self.morir("asfixia en la mina")
            return None
        
        # Verificar muerte por intoxicación (3% de probabilidad)
        if random.random() < 0.03:
            self.morir("intoxicación por gases")
            return None
        
        # Minar exitosamente
        multiplicador = self.clase.value
        cantidad = random.randint(2, 5) * multiplicador
        self.materiales_minados += cantidad
        self.ganar_experiencia(10)
        print(f"⛏️ {self.tipo} ({self.clase.name}) minó {cantidad} piedras")
        return {'recurso': 'piedra', 'cantidad': cantidad}

# ============= ENANO =============
class Enano(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Enano', '🧔', posicion)
        self.fuerza = 5
        self.cerveza_producida = 0
        
    def entrenar(self):
        """Acción de entrenar - aumenta fuerza"""
        if not self.esta_vivo():
            return False
        
        incremento = 1 * self.clase.value
        self.fuerza += incremento
        self.ganar_experiencia(5)
        print(f"💪 {self.tipo} ({self.clase.name}) entrenó. Fuerza: {self.fuerza}")
        return True
    
    def defender(self, enemigo):
        """Acción de defender - combate contra enemigos"""
        if not self.esta_vivo():
            return False
        
        poder_enano = self.fuerza * self.clase.value
        poder_enemigo = enemigo.poder_ataque
        
        print(f"⚔️ {self.tipo} (Fuerza: {poder_enano}) vs {enemigo.tipo} (Ataque: {poder_enemigo})")
        
        if poder_enano >= poder_enemigo:
            # Victoria
            enemigo.recibir_dano(poder_enano)
            self.ganar_experiencia(20)
            print(f"✅ {self.tipo} defendió exitosamente")
            return True
        else:
            # Derrota - puede morir
            diferencia = poder_enemigo - poder_enano
            if diferencia > 30:
                self.morir(f"ataque de {enemigo.tipo}")
            else:
                self.recibir_lesion(f"ataque de {enemigo.tipo}")
            return False
    
    def hacer_cerveza(self, cebada_cantidad):
        """Acción de hacer cerveza - usa cebada"""
        if not self.esta_vivo():
            return 0
        
        if cebada_cantidad < 2:
            print(f"⚠️ Se necesitan al menos 2 cebadas para hacer cerveza")
            return 0
        
        # Más eficiente según la clase
        cerveza = (cebada_cantidad // 2) * self.clase.value
        self.cerveza_producida += cerveza
        print(f"🍺 {self.tipo} ({self.clase.name}) produjo {cerveza} cervezas")
        return cerveza

# ============= LEÑADOR =============
class Lenador(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Leñador', '🪓', posicion)
        self.arboles_talados = 0
        
    def talar(self):
        """Acción de talar - puede morir por árbol caído o lesión por hacha"""
        if not self.esta_vivo():
            return None
        
        # Verificar muerte por árbol caído (7% de probabilidad)
        if random.random() < 0.07:
            self.morir("árbol caído encima")
            return None
        
        # Verificar lesión por hacha (10% de probabilidad)
        if random.random() < 0.10:
            self.recibir_lesion("corte con hacha")
        
        # Talar exitosamente
        multiplicador = self.clase.value
        cantidad = random.randint(3, 6) * multiplicador
        self.arboles_talados += 1
        self.ganar_experiencia(8)
        print(f"🪓 {self.tipo} ({self.clase.name}) taló {cantidad} maderas")
        return {'recurso': 'madera', 'cantidad': cantidad}

# ============= CONSTRUCTOR =============
class Constructor(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Constructor', '🔨', posicion)
        self.estructuras_construidas = 0
        
    def construir(self, tipo_estructura):
        """Acción de construir - puede lesionarse con el martillo"""
        if not self.esta_vivo():
            return None
        
        # Verificar lesión por martillo (8% de probabilidad)
        if random.random() < 0.08:
            self.recibir_lesion("golpe con martillo")
        
        # Construir exitosamente
        eficiencia = self.clase.value
        tiempo_construccion = max(1, 10 - (eficiencia * 2))
        self.estructuras_construidas += 1
        self.ganar_experiencia(15)
        print(f"🔨 {self.tipo} ({self.clase.name}) construyó {tipo_estructura} (tiempo: {tiempo_construccion})")
        return {'estructura': tipo_estructura, 'tiempo': tiempo_construccion}

# ============= GRANJERO =============
class Granjero(Personaje):
    def __init__(self, posicion=(0, 0)):
        super().__init__('Granjero', '👨‍🌾', posicion)
        self.cultivos_plantados = 0
        
    def cultivar(self, tipo_cultivo):
        """Acción de cultivar - planta trigo o cebada"""
        if not self.esta_vivo():
            return None
        
        multiplicador = self.clase.value
        cantidad = random.randint(4, 8) * multiplicador
        self.cultivos_plantados += 1
        self.ganar_experiencia(7)
        print(f"🌾 {self.tipo} ({self.clase.name}) cultivó {cantidad} {tipo_cultivo}")
        return {'cultivo': tipo_cultivo, 'cantidad': cantidad}
    
    def dar_comida_animales(self, animales, trigo_disponible):
        """Acción de dar de comer a los animales"""
        if not self.esta_vivo():
            return False
        
        trigo_necesario = len(animales)
        if trigo_disponible < trigo_necesario:
            print(f"⚠️ No hay suficiente trigo. Necesario: {trigo_necesario}, Disponible: {trigo_disponible}")
            return False
        
        animales_alimentados = 0
        for animal in animales:
            if animal.comer():
                animales_alimentados += 1
        
        print(f"🌾 {self.tipo} alimentó {animales_alimentados} animales")
        return True

# ============= DUENDE =============
class Duende:
    def __init__(self, posicion=(0, 0)):
        self.tipo = 'Duende'
        self.simbolo = '👹'
        self.posicion = posicion
        self.poder_ataque = random.randint(20, 35)
        self.salud = 50
        self.objetos_robados = []
        
    def atacar(self, victima):
        """Acción de atacar - puede matar"""
        if self.salud <= 0:
            return False
        
        print(f"👹 {self.tipo} ataca a {victima.tipo}")
        
        # Decidir si es ataque mortal
        if random.random() < 0.3:  # 30% de matar directamente
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        return True
    
    def robar(self, cofre):
        """Acción de robar - toma items del cofre"""
        if self.salud <= 0:
            return None
        
        if not cofre.contenido:
            print(f"👹 {self.tipo} intentó robar pero el cofre está vacío")
            return None
        
        # Robar un item aleatorio
        items = list(cofre.contenido.keys())
        item_robado = random.choice(items)
        cantidad_maxima = cofre.contenido[item_robado]
        cantidad_robada = random.randint(1, min(3, cantidad_maxima))
        
        if cofre.retirar(item_robado, cantidad_robada):
            self.objetos_robados.append((item_robado, cantidad_robada))
            print(f"👹 {self.tipo} robó {cantidad_robada} {item_robado}")
            return (item_robado, cantidad_robada)
        return None
    
    def recibir_dano(self, cantidad):
        """Recibe daño de un defensor"""
        self.salud -= cantidad
        if self.salud <= 0:
            print(f"💀 {self.tipo} fue derrotado")

# ============= ORCO =============
class Orco:
    def __init__(self, posicion=(0, 0)):
        self.tipo = 'Orco'
        self.simbolo = '👺'
        self.posicion = posicion
        self.poder_ataque = random.randint(35, 50)
        self.salud = 80
        
    def atacar(self, victima):
        """Acción de atacar - puede matar"""
        if self.salud <= 0:
            return False
        
        print(f"👺 {self.tipo} ataca ferozmente a {victima.tipo}")
        
        # Orcos tienen mayor probabilidad de matar (50%)
        if random.random() < 0.5:
            victima.morir(f"ataque de {self.tipo}")
        else:
            victima.recibir_lesion(f"ataque de {self.tipo}")
        return True
    
    def recibir_dano(self, cantidad):
        """Recibe daño de un defensor"""
        self.salud -= cantidad
        if self.salud <= 0:
            print(f"💀 {self.tipo} fue derrotado")

# ============= ANIMALES =============
class Vaca:
    def __init__(self):
        self.tipo = 'Vaca'
        self.simbolo = '🐄'
        self.hambre = 0
        self.viva = True
        self.leche_disponible = 0
        
    def comer(self):
        """Come y reduce hambre"""
        if not self.viva:
            return False
        self.hambre = max(0, self.hambre - 50)
        self.leche_disponible += 1
        return True
    
    def dar_leche(self):
        """Da leche si está bien alimentada"""
        if not self.viva or self.hambre > 50:
            return 0
        leche = self.leche_disponible
        self.leche_disponible = 0
        print(f"🥛 Vaca dio {leche} leches")
        return leche
    
    def sacrificar(self):
        """Sacrifica la vaca por recursos"""
        if not self.viva:
            return None
        self.viva = False
        print(f"🔪 Vaca sacrificada")
        return {'carne': 10, 'piel': 5, 'leche': self.leche_disponible}
    
    def atacar_personaje(self, personaje):
        """Vaca puede atacar y lesionar (5% probabilidad)"""
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
    def __init__(self):
        self.tipo = 'Gallina'
        self.simbolo = '🐔'
        self.hambre = 0
        self.viva = True
        
    def comer(self):
        """Come y reduce hambre"""
        if not self.viva:
            return False
        self.hambre = max(0, self.hambre - 50)
        return True
    
    def poner_huevo(self):
        """Pone huevos si está bien alimentada"""
        if not self.viva or self.hambre > 50:
            return 0
        huevos = random.randint(1, 3)
        print(f"🥚 Gallina puso {huevos} huevos")
        return huevos
    
    def sacrificar(self):
        """Sacrifica la gallina por recursos"""
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
    def __init__(self):
        self.tipo = 'Cerdo'
        self.simbolo = '🐷'
        self.hambre = 0
        self.vivo = True
        
    def comer(self):
        """Come y reduce hambre"""
        if not self.vivo:
            return False
        self.hambre = max(0, self.hambre - 50)
        return True
    
    def sacrificar(self):
        """Sacrifica el cerdo por recursos"""
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

# ============= CULTIVOS =============
class Trigo:
    def __init__(self):
        self.tipo = 'trigo'
        self.crecimiento = 0
        self.maduro = False
        self.uso = 'alimentar animales o hacer pan'
        
    def crecer(self, hay_lluvia=False):
        """Crece más rápido con lluvia"""
        if self.maduro:
            return
        incremento = 30 if hay_lluvia else 15
        self.crecimiento = min(100, self.crecimiento + incremento)
        if self.crecimiento >= 100:
            self.maduro = True
            print(f"🌾 Trigo está maduro para cosechar")
    
    def cosechar(self):
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
    def __init__(self):
        self.tipo = 'cebada'
        self.crecimiento = 0
        self.maduro = False
        self.uso = 'hacer cerveza'
        
    def crecer(self, hay_lluvia=False):
        """Crece más rápido con lluvia"""
        if self.maduro:
            return
        incremento = 30 if hay_lluvia else 15
        self.crecimiento = min(100, self.crecimiento + incremento)
        if self.crecimiento >= 100:
            self.maduro = True
            print(f"🌾 Cebada está madura para cosechar")
    
    def cosechar(self):
        """Cosecha la cebada madura"""
        if not self.maduro:
            print(f"⚠️ Cebada no está madura")
            return 0
        cantidad = random.randint(4, 9)
        self.maduro = False
        self.crecimiento = 0
        print(f"🌾 Cosechado {cantidad} cebadas")
        return cantidad

# ============= COFRES =============
class CofreComida:
    def __init__(self):
        self.tipo = 'Cofre de Comida y Cultivos'
        self.contenido = {}
        self.capacidad = 100
        
    def guardar(self, item, cantidad):
        """Guarda comida de animales o cultivos"""
        items_permitidos = ['carne', 'huevos', 'leche', 'trigo', 'cebada', 'pan', 'plumas', 'piel']
        
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
    
    def retirar(self, item, cantidad):
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
    def __init__(self):
        self.tipo = 'Cofre Inicial'
        self.contenido = {}
        self.capacidad = 150
        
    def guardar(self, item, cantidad):
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
    
    def retirar(self, item, cantidad):
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

# ============= CLIMA =============
class Lluvia:
    def __init__(self):
        self.tipo = 'Lluvia'
        self.simbolo = '🌧️'
        self.activa = False
        
    def activar(self):
        """Activa la lluvia"""
        self.activa = True
        print(f"🌧️ ¡Comenzó a llover!")
    
    def aplicar_efectos(self, cultivos):
        """Hace crecer los cultivos más rápido"""
        if not self.activa:
            return
        
        print(f"🌧️ La lluvia hace crecer los cultivos...")
        for cultivo in cultivos:
            cultivo.crecer(hay_lluvia=True)
    
    def detener(self):
        """Detiene la lluvia"""
        self.activa = False
        print(f"☀️ La lluvia terminó")

class Tormenta:
    def __init__(self):
        self.tipo = 'Tormenta'
        self.simbolo = '⛈️'
        self.activa = False
        self.intensidad = 0
        
    def activar(self, intensidad=5):
        """Activa la tormenta"""
        self.activa = True
        self.intensidad = intensidad
        print(f"⛈️ ¡Comenzó una tormenta! (Intensidad: {intensidad})")
    
    def aplicar_efectos(self, personajes):
        """Puede caer rayos o causar inundaciones"""
        if not self.activa:
            return
        
        # Rayos (probabilidad según intensidad)
        prob_rayo = self.intensidad * 0.1
        if random.random() < prob_rayo and personajes:
            victima = random.choice(personajes)
            if victima.esta_vivo():
                print(f"⚡ ¡Un rayo cayó!")
                victima.morir("impacto de rayo")
        
        # Inundaciones (probabilidad según intensidad)
        prob_inundacion = self.intensidad * 0.08
        if random.random() < prob_inundacion and personajes:
            afectados = random.sample(personajes, min(len(personajes), 3))
            print(f"🌊 ¡Inundación!")
            for personaje in afectados:
                if personaje.esta_vivo():
                    personaje.recibir_lesion("inundación")
    
    def detener(self):
        """Detiene la tormenta"""
        self.activa = False
        print(f"☀️ La tormenta pasó")

class Tornado:
    def __init__(self):
        self.tipo = 'Tornado'
        self.simbolo = '🌪️'
        self.activo = False
        
    def activar(self):
        """Activa el tornado"""
        self.activo = True
        print(f"🌪️ ¡TORNADO! ¡Peligro extremo!")
    
    def aplicar_efectos(self, personajes, animales, estructuras):
        """Destrucción masiva: mata animales, destruye estructuras, mata personajes"""
        if not self.activo:
            return
        
        print(f"🌪️ El tornado causa destrucción masiva...")
        
        # Matar animales (60% de probabilidad)
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
        
        # Destruir estructuras (70% de probabilidad)
        estructuras_destruidas = 0
        for estructura in estructuras:
            if random.random() < 0.7:
                estructura['destruida'] = True
                estructuras_destruidas += 1
        print(f"   🏚️ {estructuras_destruidas} estructuras destruidas")
        
        # Matar personajes (40% de probabilidad)
        personajes_muertos = 0
        for personaje in personajes:
            if personaje.esta_vivo() and random.random() < 0.4:
                personaje.morir("tornado")
                personajes_muertos += 1
        print(f"   💀 {personajes_muertos} personajes murieron")
    
    def detener(self):
        """Detiene el tornado"""
        self.activo = False
        print(f"☀️ El tornado se disipó")

