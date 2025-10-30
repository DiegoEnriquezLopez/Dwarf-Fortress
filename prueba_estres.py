import random
from personajes import (
    Minero, Lenador, Constructor, Granjero, Enano,
    Duende, Orco,
    Vaca, Gallina, Cerdo,
    CofrePrincipal, CofreAlimentos,
    Trigo, Lluvia, Tormenta, Tornado
)
from planificador import Planificador, TipoEvento
from gestion import GestorPoblacion


class EstadoJuego:
    def __init__(self):
        self.tiempo_actual = 0
        self.dia = 1
        self.recursos = {
            'madera': 0,
            'piedra': 0,
            'trigo': 0,
            'carne': 0,
            'agua': 0,
            'cerveza': 0
        }
        self.estructuras = []
        self.clima_activo = None

    def actualizar_recursos(self, recurso, cantidad):
        if recurso not in self.recursos:
            self.recursos[recurso] = 0
        self.recursos[recurso] += cantidad

    def consumir_recurso(self, recurso, cantidad):
        if self.recursos.get(recurso, 0) >= cantidad:
            self.recursos[recurso] -= cantidad
            return True
        return False

    def avanzar_tiempo(self):
        self.tiempo_actual += 1
        if self.tiempo_actual % 10 == 0:
            self.dia += 1


def crear_poblacion_inicial():
    personajes = []
    n_min = random.randint(1, 3)
    n_len = random.randint(1, 3)
    n_con = random.randint(1, 2)
    n_gra = random.randint(1, 3)
    n_ena = random.randint(1, 3)
    for _ in range(n_min):
        personajes.append(Minero((random.randint(0, 10), random.randint(0, 10))))
    for _ in range(n_len):
        personajes.append(Lenador((random.randint(0, 10), random.randint(0, 10))))
    for _ in range(n_con):
        personajes.append(Constructor((random.randint(0, 10), random.randint(0, 10))))
    for _ in range(n_gra):
        personajes.append(Granjero((random.randint(0, 10), random.randint(0, 10))))
    for _ in range(n_ena):
        personajes.append(Enano((random.randint(0, 10), random.randint(0, 10))))
    return personajes


def crear_enemigos():
    enemigos = []
    n_duendes = random.randint(1, 3)
    n_orcos = random.randint(0, 2)
    for _ in range(n_duendes):
        enemigos.append(Duende((random.randint(8, 15), random.randint(8, 15))))
    for _ in range(n_orcos):
        enemigos.append(Orco((random.randint(8, 15), random.randint(8, 15))))
    return enemigos


def crear_animales():
    animales = []
    for _ in range(random.randint(1, 2)):
        animales.append(Vaca())
    for _ in range(random.randint(1, 3)):
        animales.append(Gallina())
    for _ in range(random.randint(0, 2)):
        animales.append(Cerdo())
    return animales


def prueba_cofres():
    cofre_principal = CofrePrincipal()
    cofre_alimentos = CofreAlimentos()
    cofre_principal.inicializar_herramientas()
    return cofre_principal, cofre_alimentos


def prueba_gestor_poblacion(personajes, enemigos):
    gestor = GestorPoblacion()
    for p in personajes:
        gestor.agregar_enano(p)
    for e in enemigos:
        gestor.agregar_enemigo(e)
    return gestor


def alimentar_planificador(planificador, estado_juego):
    acciones_base = [
        ('minar', {'cantidad': random.randint(5, 15)}),
        ('talar', {'cantidad': random.randint(5, 15)}),
        ('cultivar', {'tipo': 'trigo'}),
        ('construir', {'tipo': random.choice(['casa', 'muralla', 'pozo'])}),
        ('defender', {})
    ]
    random.shuffle(acciones_base)
    for acc, params in acciones_base:
        planificador.agregar_orden_usuario(acc, params)
    if random.random() < 0.4:
        planificador.generar_ordenes_por_evento(TipoEvento.CLIMA_TORMENTA)
    if random.random() < 0.25:
        planificador.generar_ordenes_por_evento(TipoEvento.CLIMA_TORNADO)
    if random.random() < 0.35:
        duende = Duende()
        planificador.generar_ordenes_por_evento(TipoEvento.ATAQUE_ENEMIGO, {'enemigo': duende})
    if random.random() < 0.3:
        planificador.generar_ordenes_por_evento(TipoEvento.HAMBRE_CRITICA)


def prueba_acciones_personajes(personajes, cofre_principal, cofre_alimentos, estado_juego):
    mineros = [p for p in personajes if isinstance(p, Minero) and p.esta_vivo()]
    lenadores = [p for p in personajes if isinstance(p, Lenador) and p.esta_vivo()]
    granjeros = [p for p in personajes if isinstance(p, Granjero) and p.esta_vivo()]
    constructores = [p for p in personajes if isinstance(p, Constructor) and p.esta_vivo()]
    enanos = [p for p in personajes if isinstance(p, Enano) and p.esta_vivo()]
    if mineros:
        hasta = random.randint(1, len(mineros))
        for minero in mineros[:hasta]:
            resultado = minero.minar()
            if resultado:
                cofre_principal.guardar(resultado['recurso'], resultado['cantidad'])
                estado_juego.actualizar_recursos(resultado['recurso'], resultado['cantidad'])
    if lenadores:
        hasta = random.randint(1, len(lenadores))
        for lenador in lenadores[:hasta]:
            resultado = lenador.talar()
            if resultado:
                cofre_principal.guardar(resultado['recurso'], resultado['cantidad'])
                estado_juego.actualizar_recursos(resultado['recurso'], resultado['cantidad'])
    for granjero in granjeros:
        if random.random() < 0.7:
            resultado = granjero.cultivar('trigo')
            if resultado:
                cofre_alimentos.guardar(resultado['cultivo'], resultado['cantidad'])
                estado_juego.actualizar_recursos(resultado['cultivo'], resultado['cantidad'])
    if constructores:
        constructor = random.choice(constructores)
        resultado = constructor.construir(random.choice(['casa', 'granja', 'muro']))
        if resultado:
            estado_juego.estructuras.append({
                'tipo': resultado['estructura'],
                'destruida': False,
                'tiempo_construccion': resultado['tiempo'],
                'pos': (random.randint(0, 20), random.randint(0, 20))
            })
    for enano in enanos:
        if random.random() < 0.6:
            enano.entrenar()


def prueba_combate(personajes, enemigos, gestor):
    enanos = [p for p in personajes if isinstance(p, Enano) and p.esta_vivo()]
    if not enanos:
        return
    enemigos_vivos = [e for e in enemigos if e.salud > 0]
    if not enemigos_vivos:
        return
    random.shuffle(enemigos_vivos)
    limite = min(len(enanos), len(enemigos_vivos))
    for i in range(limite):
        enano = enanos[i]
        enemigo = enemigos_vivos[i]
        gano = enano.defender(enemigo)
        if gano:
            gestor.remover_enemigo(enemigo)


def prueba_animales(animales, cofre_alimentos, estado_juego):
    vivos = [a for a in animales if (a.viva if hasattr(a, 'viva') else a.vivo)]
    for animal in vivos:
        animal.comer()
    for animal in vivos:
        if hasattr(animal, 'beber'):
            animal.beber()
    for animal in animales:
        if isinstance(animal, Vaca) and animal.viva:
            leche = animal.dar_leche()
            if leche > 0:
                cofre_alimentos.guardar('leche', leche)
                estado_juego.actualizar_recursos('leche', leche)
        elif isinstance(animal, Gallina) and animal.viva:
            huevos = animal.poner_huevo()
            if huevos > 0:
                cofre_alimentos.guardar('huevos', huevos)
                estado_juego.actualizar_recursos('huevos', huevos)
    for animal in animales:
        animal.actualizar()


def prueba_clima(personajes, animales, estado_juego):
    cultivos = [Trigo(), Trigo(), Trigo()]
    if random.random() < 0.5:
        lluvia = Lluvia()
        lluvia.activar()
        lluvia.aplicar_efectos(cultivos)
        lluvia.detener()
    personajes_vivos = [p for p in personajes if p.esta_vivo()]
    if random.random() < 0.4:
        tormenta = Tormenta()
        tormenta.activar(intensidad=random.randint(3, 7))
        tormenta.aplicar_efectos(personajes_vivos)
        tormenta.detener()
    if random.random() < 0.25:
        tornado = Tornado()
        tornado.activar()
        tornado.aplicar_efectos(personajes_vivos, animales, estado_juego.estructuras)
        tornado.detener()


def prueba_niveles_experiencia(personajes):
    mineros = [p for p in personajes if isinstance(p, Minero) and p.esta_vivo()]
    if not mineros:
        return
    minero = random.choice(mineros)
    repeticiones = random.randint(8, 15)
    for _ in range(repeticiones):
        if minero.esta_vivo():
            minero.minar()


def prueba_necesidades(personajes, cofre_alimentos):
    enanos = [p for p in personajes if isinstance(p, Enano) and p.esta_vivo()]
    if not enanos:
        return
    enano = random.choice(enanos)
    for _ in range(15):
        enano.actualizar_necesidades()
    if cofre_alimentos.retirar('carne', 1):
        enano.comer()
    enano.beber('agua')


def ejecutar_todas_las_pruebas():
    personajes = crear_poblacion_inicial()
    enemigos = crear_enemigos()
    animales = crear_animales()
    estado_juego = EstadoJuego()
    cofre_principal, cofre_alimentos = prueba_cofres()
    gestor = prueba_gestor_poblacion(personajes, enemigos)
    planificador = Planificador(gestor, estado_juego)
    alimentar_planificador(planificador, estado_juego)
    planificador.procesar_ciclo()
    prueba_acciones_personajes(personajes, cofre_principal, cofre_alimentos, estado_juego)
    prueba_combate(personajes, enemigos, gestor)
    prueba_animales(animales, cofre_alimentos, estado_juego)
    prueba_clima(personajes, animales, estado_juego)
    gestor.limpiar_muertos()
    prueba_niveles_experiencia(personajes)
    prueba_necesidades(personajes, cofre_alimentos)
    ciclos = 0
    while len(planificador.acciones_ejecutadas) < 50 and ciclos < 20:
        estado_juego.avanzar_tiempo()
        gestor.actualizar_poblacion()
        alimentar_planificador(planificador, estado_juego)
        planificador.procesar_ciclo()
        prueba_acciones_personajes(personajes, cofre_principal, cofre_alimentos, estado_juego)
        prueba_animales(animales, cofre_alimentos, estado_juego)
        prueba_clima(personajes, animales, estado_juego)
        gestor.limpiar_muertos()
        ciclos += 1
    planificador.mostrar_estado()
    gestor.mostrar_estado()


if __name__ == "__main__":
    ejecutar_todas_las_pruebas()
