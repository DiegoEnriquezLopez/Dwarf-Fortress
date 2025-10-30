from personajes import *
from planificador import Planificador, TipoEvento
from gestion import GestorPoblacion
import random


class EstadoJuego:
    def __init__(self):
        self.tiempo_actual = 0
        self.dia = 1
        self.recursos = {
            'madera': 5,
            'piedra': 5,
            'trigo': 10,
            'carne': 5,
            'agua': 20,
            'cerveza': 0
        }
        self.estructuras = []
        self.clima_activo = None
    
    def actualizar_recursos(self, recurso, cantidad):
        """Actualiza la cantidad de un recurso"""
        if recurso not in self.recursos:
            self.recursos[recurso] = 0
        self.recursos[recurso] += cantidad
    
    def consumir_recurso(self, recurso, cantidad):
        """Consume recursos si hay suficientes"""
        if self.recursos.get(recurso, 0) >= cantidad:
            self.recursos[recurso] -= cantidad
            return True
        return False
    
    def avanzar_tiempo(self):
        """Avanza el tiempo del juego"""
        self.tiempo_actual += 1
        if self.tiempo_actual % 10 == 0:
            self.dia += 1
            print(f"\n📅 Día {self.dia}")


def crear_poblacion_inicial():
    print("\n🏗️ CREANDO POBLACIÓN INICIAL...")
    personajes = [
        Minero((1, 1)),
        Minero((2, 1)),
        Lenador((3, 1)),
        Lenador((4, 1)),
        Constructor((5, 1)),
        Granjero((6, 1)),
        Granjero((7, 1)),
        Enano((8, 1)),
        Enano((9, 1))
    ]
    print(f"✅ {len(personajes)} personajes creados")
    for p in personajes:
        print(f"  - {p}")
    return personajes


def crear_enemigos():
    print("\n👹 CREANDO ENEMIGOS...")
    enemigos = [
        Duende((10, 10)),
        Duende((12, 8)),
        Orco((15, 15))
    ]
    print(f"✅ {len(enemigos)} enemigos creados")
    for e in enemigos:
        print(f"  - {e.tipo} (Ataque: {e.poder_ataque}, Salud: {e.salud})")
    return enemigos


def crear_animales():
    print("\n🐄 CREANDO ANIMALES...")
    animales = [
        Vaca(),
        Vaca(),
        Gallina(),
        Gallina(),
        Gallina(),
        Cerdo()
    ]
    print(f"✅ {len(animales)} animales creados")
    return animales


def prueba_cofres():
    print("\n" + "="*60)
    print("🧪 PRUEBA 1: COFRES Y ESTRUCTURAS DE DATOS")
    print("="*60)
    
    cofre_principal = CofrePrincipal()
    cofre_alimentos = CofreAlimentos()
    
    print("\n📦 Inicializando herramientas en cofre principal...")
    cofre_principal.inicializar_herramientas()
    
    print("\n📥 Guardando recursos en cofre principal (Queue)...")
    cofre_principal.guardar('madera', 20)
    cofre_principal.guardar('piedra', 15)
    cofre_principal.guardar('madera', 10)
    
    print("\n📥 Guardando alimentos en cofre alimentos (Deque)...")
    cofre_alimentos.guardar('carne', 10)
    cofre_alimentos.guardar('trigo', 15)
    cofre_alimentos.guardar('huevos', 8)
    cofre_alimentos.guardar('leche', 5)
    
    print("\n📋 Estado inicial de cofres:")
    cofre_principal.ver_inventario()
    cofre_alimentos.ver_inventario()
    
    print("\n📤 Retirando recursos (FIFO - Queue)...")
    cofre_principal.retirar('madera', 5)
    
    print("\n📤 Retirando alimentos (FIFO - Deque por frescura)...")
    cofre_alimentos.retirar('carne', 3)
    
    print("\n🔄 Simulando paso del tiempo (degradación de frescura)...")
    for i in range(3):
        print(f"  Ciclo {i+1}...")
        cofre_alimentos.actualizar_frescura()
    
    print("\n📋 Estado después de degradación:")
    cofre_alimentos.ver_inventario()
    
    print("\n🚫 Prueba: Intentando guardar items de ENEMIGOS...")
    duende = Duende()
    resultado = cofre_principal.guardar_herramienta('espada_enemiga', 1, de_personaje=duende)
    if not resultado:
        print("✅ Correcto: NO se permiten items de enemigos")
    
    print("\n✅ Prueba: Guardando herramienta de personaje de la aldea...")
    minero = Minero()
    resultado = cofre_principal.guardar_herramienta('pico', 1, de_personaje=minero)
    if resultado:
        print("✅ Correcto: Se permiten items de la aldea")
    
    return cofre_principal, cofre_alimentos


def prueba_gestor_poblacion(personajes, enemigos):
    print("\n" + "="*60)
    print("🧪 PRUEBA 2: GESTOR DE POBLACIÓN CON DEQUE")
    print("="*60)
    
    gestor = GestorPoblacion()
    
    print("\n👥 Agregando personajes al gestor...")
    for p in personajes:
        gestor.agregar_enano(p)
    
    print("\n👹 Agregando enemigos al gestor...")
    for e in enemigos:
        gestor.agregar_enemigo(e)
    
    gestor.mostrar_estado()
    
    print("\n🔍 Probando búsqueda por compatibilidad...")
    acciones = ['minar', 'talar', 'construir', 'cultivar', 'defender']
    
    for accion in acciones:
        mejor = gestor.obtener_mejor_enano_para(accion)
        if mejor:
            comp = mejor.calcular_compatibilidad(accion)
            print(f"  {accion}: {mejor.tipo} (compatibilidad: {comp:.1f})")
    
    print("\n⚙️ Probando marcar ocupado/liberar...")
    enano = gestor.obtener_enano_disponible()
    if enano:
        print(f"  Obtenido: {enano.tipo}")
        accion = {'tipo': 'minar', 'duracion': 5}
        gestor.marcar_ocupado(enano, accion)
        print(f"  Marcado como ocupado")
        
        gestor.mostrar_estado()
        
        enano.tiempo_ocupado = 0
        gestor.liberar_enano(enano)
        print(f"  Liberado")
        
        gestor.mostrar_estado()
    
    return gestor


def prueba_planificador(gestor, estado_juego):
    print("\n" + "="*60)
    print("🧪 PRUEBA 3: PLANIFICADOR (Queue → Heap → Ejecución)")
    print("="*60)
    
    planificador = Planificador(gestor, estado_juego)
    
    print("\n📥 Agregando órdenes del usuario al BUFFER (Queue)...")
    planificador.agregar_orden_usuario('minar', {'cantidad': 10})
    planificador.agregar_orden_usuario('talar', {'cantidad': 10})
    planificador.agregar_orden_usuario('cultivar', {'tipo': 'trigo'})
    planificador.agregar_orden_usuario('construir', {'tipo': 'casa'})
    planificador.agregar_orden_usuario('defender', {})
    
    print("\n⛈️ Generando evento automático: TORMENTA...")
    planificador.generar_ordenes_por_evento(TipoEvento.CLIMA_TORMENTA)
    
    print("\n🌪️ Generando evento automático: TORNADO...")
    planificador.generar_ordenes_por_evento(TipoEvento.CLIMA_TORNADO)
    
    print("\n👹 Generando evento automático: ATAQUE ENEMIGO...")
    duende = Duende()
    planificador.generar_ordenes_por_evento(
        TipoEvento.ATAQUE_ENEMIGO, 
        {'enemigo': duende}
    )
    
    print("\n🍖 Generando evento automático: HAMBRE CRÍTICA...")
    planificador.generar_ordenes_por_evento(TipoEvento.HAMBRE_CRITICA)
    
    print("\n⚙️ PROCESANDO CICLO DEL PLANIFICADOR...")
    print("  1. Sacar órdenes del buffer (Queue)")
    print("  2. Calcular prioridades con algoritmo de decisión")
    print("  3. Meter tareas al heap (QHeap)")
    print("  4. Despachar acciones con mejor puntaje")
    print()
    
    planificador.procesar_ciclo()
    
    planificador.mostrar_estado()
    
    return planificador


def prueba_acciones_personajes(personajes, cofre_principal, cofre_alimentos, estado_juego):
    print("\n" + "="*60)
    print("🧪 PRUEBA 4: ACCIONES DE PERSONAJES")
    print("="*60)
    
    print("\n⛏️ MINERO minando...")
    mineros = [p for p in personajes if isinstance(p, Minero) and p.esta_vivo()]
    if mineros:
        for minero in mineros[:2]:
            resultado = minero.minar()
            if resultado:
                cofre_principal.guardar(resultado['recurso'], resultado['cantidad'])
                estado_juego.actualizar_recursos(resultado['recurso'], resultado['cantidad'])
    
    print("\n🪓 LEÑADOR talando...")
    lenadores = [p for p in personajes if isinstance(p, Lenador) and p.esta_vivo()]
    if lenadores:
        for lenador in lenadores[:2]:
            resultado = lenador.talar()
            if resultado:
                cofre_principal.guardar(resultado['recurso'], resultado['cantidad'])
                estado_juego.actualizar_recursos(resultado['recurso'], resultado['cantidad'])
    
    print("\n🌾 GRANJERO cultivando...")
    granjeros = [p for p in personajes if isinstance(p, Granjero) and p.esta_vivo()]
    if granjeros:
        for granjero in granjeros:
            resultado = granjero.cultivar('trigo')
            if resultado:
                cofre_alimentos.guardar(resultado['cultivo'], resultado['cantidad'])
                estado_juego.actualizar_recursos(resultado['cultivo'], resultado['cantidad'])
    
    print("\n🔨 CONSTRUCTOR construyendo...")
    constructores = [p for p in personajes if isinstance(p, Constructor) and p.esta_vivo()]
    if constructores:
        constructor = constructores[0]
        resultado = constructor.construir('casa')
        if resultado:
            estado_juego.estructuras.append({
                'tipo': resultado['estructura'],
                'destruida': False,
                'tiempo_construccion': resultado['tiempo']
            })
    
    print("\n💪 ENANO entrenando...")
    enanos = [p for p in personajes if isinstance(p, Enano) and p.esta_vivo()]
    if enanos:
        for enano in enanos:
            enano.entrenar()
    
    print("\n🍺 ENANO haciendo cerveza...")
    if enanos and estado_juego.recursos.get('trigo', 0) >= 4:
        enano = enanos[0]
        trigo_usado = 4
        cerveza = enano.hacer_cerveza(trigo_usado)
        if cerveza > 0:
            estado_juego.consumir_recurso('trigo', trigo_usado)
            estado_juego.actualizar_recursos('cerveza', cerveza)
            cofre_alimentos.retirar('trigo', trigo_usado)
            cofre_alimentos.guardar('cerveza', cerveza)
    
    print("\n📋 Estado de cofres después de acciones:")
    cofre_principal.ver_inventario()
    cofre_alimentos.ver_inventario()
    
    print(f"\n📊 Recursos totales del juego:")
    for recurso, cantidad in estado_juego.recursos.items():
        print(f"  {recurso}: {cantidad}")


def prueba_combate(personajes, enemigos, gestor):
    print("\n" + "="*60)
    print("🧪 PRUEBA 5: SISTEMA DE COMBATE")
    print("="*60)
    
    enanos = [p for p in personajes if isinstance(p, Enano) and p.esta_vivo()]
    if not enanos:
        print("❌ No hay enanos disponibles para combate")
        return
    
    enemigos_vivos = [e for e in enemigos if e.salud > 0]
    if not enemigos_vivos:
        print("✅ No hay enemigos que combatir")
        return
    
    for i, enemigo in enumerate(enemigos_vivos[:2]):
        if i < len(enanos):
            enano = enanos[i]
            print(f"\n⚔️ COMBATE {i+1}:")
            print(f"  {enano.tipo} (Fuerza: {enano.fuerza}, Salud: {enano.salud})")
            print(f"  vs")
            print(f"  {enemigo.tipo} (Ataque: {enemigo.poder_ataque}, Salud: {enemigo.salud})")
            print()
            
            resultado = enano.defender(enemigo)
            
            if resultado:
                print(f"  ✅ {enano.tipo} GANÓ")
                gestor.remover_enemigo(enemigo)
            else:
                print(f"  ❌ {enano.tipo} PERDIÓ o fue herido")
            
            print(f"\n  Estado final:")
            print(f"    {enano.tipo}: Salud={enano.salud}, Estado={enano.estado.value}")
            print(f"    {enemigo.tipo}: Salud={enemigo.salud}")


def prueba_animales(animales, cofre_alimentos, estado_juego):
    print("\n" + "="*60)
    print("🧪 PRUEBA 6: SISTEMA DE ANIMALES")
    print("="*60)
    
    print("\n🌾 Alimentando animales...")
    animales_vivos = [a for a in animales if (a.viva if hasattr(a, 'viva') else a.vivo)]
    for animal in animales_vivos:
        animal.comer()
    
    print("\n💧 Dando agua a animales...")
    for animal in animales_vivos:
        if hasattr(animal, 'beber'):
            animal.beber()
    
    print("\n🥛 Vacas produciendo leche...")
    for animal in animales:
        if isinstance(animal, Vaca) and animal.viva:
            leche = animal.dar_leche()
            if leche > 0:
                cofre_alimentos.guardar('leche', leche)
                estado_juego.actualizar_recursos('leche', leche)
    
    print("\n🥚 Gallinas poniendo huevos...")
    for animal in animales:
        if isinstance(animal, Gallina) and animal.viva:
            huevos = animal.poner_huevo()
            if huevos > 0:
                cofre_alimentos.guardar('huevos', huevos)
                estado_juego.actualizar_recursos('huevos', huevos)
    
    print("\n⏰ Actualizando estado de animales (hambre/sed aumenta)...")
    for animal in animales:
        animal.actualizar()
    
    print("\n📊 Estado de animales:")
    vivos = sum(1 for a in animales if (a.viva if hasattr(a, 'viva') else a.vivo))
    print(f"  Vivos: {vivos}/{len(animales)}")
    
    print("\n📋 Cofre de alimentos:")
    cofre_alimentos.ver_inventario()


def prueba_clima(personajes, animales, estado_juego):
    print("\n" + "="*60)
    print("🧪 PRUEBA 7: SISTEMA CLIMÁTICO")
    print("="*60)
    
    cultivos = [Trigo(), Trigo(), Trigo()]
    
    print("\n🌧️ Activando LLUVIA...")
    lluvia = Lluvia()
    lluvia.activar()
    lluvia.aplicar_efectos(cultivos)
    lluvia.detener()
    
    print("\n⛈️ Activando TORMENTA (intensidad 5)...")
    personajes_vivos = [p for p in personajes if p.esta_vivo()]
    print(f"  Personajes vivos antes: {len(personajes_vivos)}")
    
    tormenta = Tormenta()
    tormenta.activar(intensidad=5)
    tormenta.aplicar_efectos(personajes_vivos)
    tormenta.detener()
    
    personajes_vivos_despues = [p for p in personajes if p.esta_vivo()]
    print(f"  Personajes vivos después: {len(personajes_vivos_despues)}")
    
    print("\n🌪️ Activando TORNADO...")
    estructuras = estado_juego.estructuras
    print(f"  Estructuras antes: {len(estructuras)}")
    print(f"  Animales vivos antes: {sum(1 for a in animales if (a.viva if hasattr(a, 'viva') else a.vivo))}")
    
    tornado = Tornado()
    tornado.activar()
    tornado.aplicar_efectos(personajes_vivos_despues, animales, estructuras)
    tornado.detener()
    
    print(f"\n📊 Bajas del TORNADO:")
    muertos = sum(1 for p in personajes if not p.esta_vivo())
    print(f"  ☠️ Personajes muertos totales: {muertos}")
    animales_muertos = sum(1 for a in animales if not (a.viva if hasattr(a, 'viva') else a.vivo))
    print(f"  ☠️ Animales muertos: {animales_muertos}")
    estructuras_destruidas = sum(1 for e in estructuras if e.get('destruida', False))
    print(f"  🏚️ Estructuras destruidas: {estructuras_destruidas}/{len(estructuras)}")


def prueba_niveles_experiencia(personajes):
    print("\n" + "="*60)
    print("🧪 PRUEBA 8: SISTEMA DE NIVELES Y EXPERIENCIA")
    print("="*60)
    
    minero = next((p for p in personajes if isinstance(p, Minero) and p.esta_vivo()), None)
    if not minero:
        print("❌ No hay minero disponible")
        return
    
    print(f"\n📊 Estado inicial de {minero.tipo}:")
    print(f"  Nivel: {minero.nivel}")
    print(f"  Clase: {minero.clase.name}")
    print(f"  Experiencia: {minero.experiencia}")
    
    print(f"\n⛏️ Minando repetidamente para ganar XP...")
    for i in range(15):
        if minero.esta_vivo():
            resultado = minero.minar()
            if resultado:
                print(f"  Ciclo {i+1}: +10 XP (Total: {minero.experiencia})")
    
    print(f"\n📊 Estado final de {minero.tipo}:")
    print(f"  Nivel: {minero.nivel}")
    print(f"  Clase: {minero.clase.name}")
    print(f"  Experiencia: {minero.experiencia}")


def prueba_necesidades(personajes, cofre_alimentos):
    print("\n" + "="*60)
    print("🧪 PRUEBA 9: SISTEMA DE NECESIDADES (Hambre/Sed/Sentimientos)")
    print("="*60)
    
    enano = next((p for p in personajes if isinstance(p, Enano) and p.esta_vivo()), None)
    if not enano:
        print("❌ No hay enano disponible")
        return
    
    print(f"\n📊 Estado inicial de {enano.tipo}:")
    print(f"  Hambre: {enano.hambre}/100")
    print(f"  Sed: {enano.sed}/100")
    print(f"  Energía: {enano.energia}/100")
    print(f"  Sentimiento: {enano.sentimiento.value}")
    
    print(f"\n⏰ Simulando 15 turnos sin comer/beber...")
    for i in range(15):
        enano.actualizar_necesidades()
        if i % 5 == 4:
            print(f"  Turno {i+1}: Hambre={enano.hambre}, Sed={enano.sed}, Sentimiento={enano.sentimiento.value}")
    
    print(f"\n📊 Después de 15 turnos:")
    print(f"  Hambre: {enano.hambre}/100")
    print(f"  Sed: {enano.sed}/100")
    print(f"  Sentimiento: {enano.sentimiento.value}")
    
    print(f"\n🍖 Alimentando al enano...")
    if cofre_alimentos.retirar('carne', 1):
        enano.comer()
    
    print(f"\n💧 Dando agua al enano...")
    enano.beber('agua')
    
    print(f"\n🍺 Dando cerveza al enano...")
    if cofre_alimentos.recursos.get('cerveza', 0) > 0:
        enano.beber('cerveza')
    
    print(f"\n📊 Estado final:")
    print(f"  Hambre: {enano.hambre}/100")
    print(f"  Sed: {enano.sed}/100")
    print(f"  Energía: {enano.energia}/100")
    print(f"  Sentimiento: {enano.sentimiento.value}")


def ejecutar_todas_las_pruebas():
    print("\n" + "="*70)
    print("🚀 INICIANDO PRUEBA DE ESTRÉS COMPLETA DEL SISTEMA")
    print("="*70)
    
    personajes = crear_poblacion_inicial()
    enemigos = crear_enemigos()
    animales = crear_animales()
    estado_juego = EstadoJuego()
    
    cofre_principal, cofre_alimentos = prueba_cofres()
    
    gestor = prueba_gestor_poblacion(personajes, enemigos)
    
    planificador = prueba_planificador(gestor, estado_juego)
    
    prueba_acciones_personajes(personajes, cofre_principal, cofre_alimentos, estado_juego)
    
    prueba_combate(personajes, enemigos, gestor)
    
    prueba_animales(animales, cofre_alimentos, estado_juego)
    
    prueba_clima(personajes, animales, estado_juego)
    
    gestor.limpiar_muertos()
    
    prueba_niveles_experiencia(personajes)
    
    prueba_necesidades(personajes, cofre_alimentos)
    
    print("\n" + "="*70)
    print("✅ PRUEBA DE ESTRÉS COMPLETADA")
    print("="*70)
    print("\n📊 RESUMEN FINAL:")
    print(f"\n👥 PERSONAJES:")
    print(f"  Total: {len(personajes)}")
    print(f"  Vivos: {sum(1 for p in personajes if p.esta_vivo())}")
    print(f"  Muertos: {sum(1 for p in personajes if not p.esta_vivo())}")
    
    print(f"\n🐄 ANIMALES:")
    print(f"  Total: {len(animales)}")
    vivos_animales = sum(1 for a in animales if (a.viva if hasattr(a, 'viva') else a.vivo))
    print(f"  Vivos: {vivos_animales}")
    print(f"  Muertos: {len(animales) - vivos_animales}")
    
    print(f"\n👹 ENEMIGOS:")
    print(f"  Total: {len(enemigos)}")
    print(f"  Derrotados: {sum(1 for e in enemigos if e.salud <= 0)}")
    print(f"  Activos: {sum(1 for e in enemigos if e.salud > 0)}")
    
    print(f"\n📦 ESTADO DEL GESTOR:")
    gestor.mostrar_estado()
    
    print(f"\n⚙️ ESTADO DEL PLANIFICADOR:")
    planificador.mostrar_estado()
    
    print(f"\n🏗️ ESTRUCTURAS: {len(estado_juego.estructuras)}")
    
    print("\n" + "="*70)
    print("🎉 TODAS LAS PRUEBAS EJECUTADAS EXITOSAMENTE")
    print("="*70)


if __name__ == "__main__":
    ejecutar_todas_las_pruebas()
