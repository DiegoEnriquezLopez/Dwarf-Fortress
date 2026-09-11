# prueba_estres.py
import random
from ListaEnlazada import to_list
from personajes import Minero, Lenador, Granjero, Constructor, Enano
from selector_personajes import seleccionar_personaje_inteligente
from planificador import TipoEvento

ACCIONES_STRESS = [
    "minar",
    "talar",
    "plantar",
    "cosechar",
    "ordeñar",
    "huevos",
    "comer",
]

TOTAL_PERSONAJES_STRESS = 60
TOTAL_ACCIONES_STRESS = 60


def _contar_actuales(game):
    c = 0
    for _ in to_list(game.characters_visual):
        c += 1
    return c


def _crear_personaje_para(game, tipo, idx):
    if hasattr(game, "walk_bounds"):
        x = random.randint(game.walk_bounds.left, game.walk_bounds.right)
        y = random.randint(game.walk_bounds.top, game.walk_bounds.bottom)
    else:
        x, y = 500 + idx * 3, 360 + idx * 2

    if tipo == "minero":
        pj = Minero(posicion=(x, y))
        game.add_character_from_personaje(pj, "minero.gif", 0.4, f"ST-MIN-{idx}")
    elif tipo == "lenador":
        pj = Lenador(posicion=(x, y))
        game.add_character_from_personaje(pj, "lenhador.gif", 0.3, f"ST-LEÑ-{idx}")
    elif tipo == "granjero":
        pj = Granjero(posicion=(x, y))
        game.add_character_from_personaje(pj, "granjero.gif", 0.3, f"ST-GRA-{idx}")
    elif tipo == "constructor":
        pj = Constructor(posicion=(x, y))
        game.add_character_from_personaje(pj, "constructor.gif", 0.25, f"ST-CON-{idx}")
    else:
        pj = Enano(posicion=(x, y))
        game.add_character_from_personaje(pj, "enano.gif", 0.22, f"ST-ENA-{idx}")

    game.gestor.agregar_enano(pj)


def _asegurar_60_personajes(game):
    actuales = _contar_actuales(game)
    faltan = TOTAL_PERSONAJES_STRESS - actuales
    if faltan <= 0:
        return
    tipos = ["minero", "lenador", "granjero", "constructor", "enano"]
    for i in range(faltan):
        t = tipos[i % len(tipos)]
        _crear_personaje_para(game, t, actuales + i)
    if hasattr(game, "_sync_menu"):
        game._sync_menu()
    if hasattr(game, "terminal"):
        game.terminal.log(f"▶ Stress: se crearon {faltan} personajes (total={TOTAL_PERSONAJES_STRESS})")


def ejecutar_prueba_estres(game, n_acciones=TOTAL_ACCIONES_STRESS):
    """
    - Crea hasta 60 personajes si faltan.
    - Intenta ejecutar n_acciones.
    - Si en ese momento no hay personaje libre → re-encola la acción.
    """
    _asegurar_60_personajes(game)

    ok = 0
    reencoladas = 0

    for i in range(n_acciones):
        accion = random.choice(ACCIONES_STRESS)

        game.planificador.registrar_evento(
            TipoEvento.ORDEN_USUARIO,
            {"accion": accion, "parametros": {}}
        )
        game.planificador.procesar_buffer()
        tarea = game.planificador.obtener_siguiente_tarea()
        if not tarea:
            game.planificador.registrar_evento(
                TipoEvento.ORDEN_USUARIO,
                {"accion": accion, "parametros": {}}
            )
            reencoladas += 1
            continue

        pj = seleccionar_personaje_inteligente(game.gestor, accion)
        if pj is None:
            game.planificador.registrar_evento(
                TipoEvento.ORDEN_USUARIO,
                {"accion": accion, "parametros": {}}
            )
            reencoladas += 1
            continue

        visual_obj = None
        for v in to_list(game.characters_visual):
            if v["personaje"] == pj:
                visual_obj = v
                break

        if visual_obj is None:
            game.planificador.registrar_evento(
                TipoEvento.ORDEN_USUARIO,
                {"accion": accion, "parametros": {}}
            )
            reencoladas += 1
            continue

        game._assign_task_to_visual(visual_obj, tarea)
        ok += 1

    if hasattr(game, "terminal"):
        game.terminal.log(f"✅ Stress terminado: hechas={ok}, reencoladas={reencoladas}")
        game.terminal.log(
            f"📦 madera={game.inv_mats.get('madera',0)}  "
            f"piedra={game.inv_mats.get('piedra',0)}  "
            f"leche={game.inv_food.get('leche',0)}  "
            f"huevos={game.inv_food.get('huevos',0)}  "
            f"trigo={game.inv_food.get('trigo',0)}"
        )
    else:
        print("Stress OK:", ok, "reencoladas:", reencoladas)
