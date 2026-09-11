# -*- coding: utf-8 -*-
import sys
import random
import pygame
import pygame_gui
from PIL import Image
import math

from gestion import GestorPoblacion
from planificador import PlanificadorTareas, TipoEvento
from personajes import (
    Enano, Minero, Lenador, Granjero, Constructor,
    CofrePrincipal, CofreAlimentos, Bar
)
from ListaEnlazada import LinkedList, to_list, length
from deque import Deque
from game_queue import Queue

try:
    from selector_personajes import seleccionar_personaje_inteligente, SelectorPersonajes
except Exception:
    seleccionar_personaje_inteligente = None

    class SelectorPersonajes:
        def __init__(self, g): ...
        def diagnosticar_candidatos(self, t): ...

from prueba_estres import ejecutar_prueba_estres

W, H = 1024, 640
FPS = 60
BG_COLOR = (28, 33, 40)

MAP_TILES = [
    ["map.jpg", "map.jpg", "map.jpg", "map.jpg"],
    ["map.jpg", "map.jpg", "map.jpg", "map.jpg"],
    ["map.jpg", "map.jpg", "map.jpg", "map.jpg"],
    ["map.jpg", "map.jpg", "map.jpg", "map.jpg"]
]

pygame.init()
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Village Builder - Con Terminal de Logs")
clock = pygame.time.Clock()

NOMBRES_ENANOS = ["Thorin", "Gimli", "Balin", "Dwalin", "Bombur", "Fili", "Kili", "Oin", "Gloin", "Bifur", "Bofur", "Dori", "Nori", "Ori"]
NOMBRES_MINEROS = ["Pedro", "Juan", "Carlos", "Miguel", "Luis", "Raúl", "Mario", "Tomas", "Erick", "Jorge"]
NOMBRES_LENADORES = ["Ragnar", "Ulf", "Bjorn", "Erik", "Leif", "Hakon", "Sven"]
NOMBRES_GRANJEROS = ["Paco", "Chuy", "Toño", "Lalo", "Pancho", "Memo", "Chava"]
NOMBRES_CONSTRUCTORES = ["Hector", "Bruno", "Marco", "Diego", "Leo", "Rafa"]


class Camera:
    def __init__(self, world_width, world_height, screen_width, screen_height):
        self.world_width = world_width
        self.world_height = world_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = world_width / 2
        self.y = world_height / 2
        self.zoom = 1.0
        self.min_zoom = 0.8
        self.max_zoom = 2.5
        self.move_speed = 300

    def update(self, dt, keys):
        move_amount = self.move_speed * dt / self.zoom
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= move_amount
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += move_amount
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= move_amount
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += move_amount

        half_view_w = (self.screen_width / self.zoom) / 2
        half_view_h = (self.screen_height / self.zoom) / 2

        self.x = max(half_view_w, min(self.world_width - half_view_w, self.x))
        self.y = max(half_view_h, min(self.world_height - half_view_h, self.y))

    def zoom_in(self):
        self.zoom = min(self.max_zoom, self.zoom * 1.1)

    def zoom_out(self):
        self.zoom = max(self.min_zoom, self.zoom / 1.1)

    def world_to_screen(self, world_x, world_y):
        view_left = self.x - (self.screen_width / self.zoom) / 2
        view_top = self.y - (self.screen_height / self.zoom) / 2
        rel_x = (world_x - view_left) * self.zoom
        rel_y = (world_y - view_top) * self.zoom
        return rel_x, rel_y

    def get_view_rect(self):
        half_w = (self.screen_width / self.zoom) / 2
        half_h = (self.screen_height / self.zoom) / 2
        return pygame.Rect(
            self.x - half_w,
            self.y - half_h,
            self.screen_width / self.zoom,
            self.screen_height / self.zoom
        )

    def is_visible(self, world_rect):
        return self.get_view_rect().colliderect(world_rect)


def load_gif_frames(path, scale=1.0):
    frames = []
    try:
        pil_img = Image.open(path)
        while True:
            frame = pil_img.convert("RGBA")
            pg_img = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
            if scale != 1.0:
                w, h = pg_img.get_size()
                pg_img = pygame.transform.smoothscale(pg_img, (int(w * scale), int(h * scale)))
            frames.append(pg_img)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
    except Exception as e:
        print(f"[Error al cargar GIF] {path}: {e}")
    if not frames:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 200, 200, 255), surf.get_rect(), 2)
        frames = [surf]
    return frames


def find_valid_position(img_rect, obj_type, safe_x, safe_y, existing_objects, distance_rules, max_attempts=100):
    i_try = 0
    while i_try < max_attempts:
        x = random.randint(safe_x[0], safe_x[1])
        y = random.randint(safe_y[0], safe_y[1])
        test_rect = img_rect.copy()
        test_rect.topleft = (x, y)
        col = False
        ex_list = existing_objects
        j = 0
        ex_len = len(ex_list)
        while j < ex_len:
            rect, t = ex_list[j]
            key = tuple(sorted([obj_type, t]))
            dist = distance_rules.get(key, 50)
            if rect.inflate(dist * 2, dist * 2).colliderect(test_rect):
                col = True
                break
            j += 1
        if not col:
            return (x, y), test_rect
        i_try += 1
    return (random.randint(safe_x[0], safe_x[1]),
            random.randint(safe_y[0], safe_y[1])), None


def obj_rect(obj):
    return obj["image"].get_rect(topleft=obj["pos"])


def character_anchor(visual):
    frame = visual["frames"][visual.get("frame_index", 0)]
    w, h = frame.get_size()
    x, y = visual["pos"]
    return x + w * 0.5, y + h * 0.85


class TerminalLogs:
    def __init__(self, max_lines=200):
        self.max_lines = max_lines
        self.lines = LinkedList()
        self.font_title = pygame.font.SysFont("consolas", 17, bold=True)
        self.font = pygame.font.SysFont("consolas", 15)
        self.visible = True
        self.panel_rect = pygame.Rect(6, 80, 260, 270)
        self.header_rect = pygame.Rect(6, 50, 120, 28)

    def log(self, text):
        self.lines.add(text)
        total = length(self.lines)
        if total > self.max_lines:
            items = to_list(self.lines)
            nueva = LinkedList()
            start = total - self.max_lines
            i = start
            while i < total:
                nueva.add(items[i])
                i += 1
            self.lines = nueva

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            if self.header_rect.collidepoint(mx, my):
                self.visible = not self.visible
                return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, (15, 140, 75), self.header_rect, border_radius=6)
        title = self.font_title.render("LOGS [!]", True, (240, 240, 240))
        surf.blit(title, (self.header_rect.x + 6, self.header_rect.y + 4))
        if not self.visible:
            return
        pygame.draw.rect(surf, (6, 18, 28, 210), self.panel_rect, border_radius=10)
        pygame.draw.rect(surf, (90, 200, 255), self.panel_rect, 2, border_radius=10)
        lines = to_list(self.lines)
        total = length(self.lines)
        y = self.panel_rect.y + 10
        start = 0
        if total > 14:
            start = total - 14
        i = start
        while i < total:
            line = lines[i]
            txt = self.font.render(line, True, (220, 240, 255))
            surf.blit(txt, (self.panel_rect.x + 8, y))
            y += 17
            i += 1


class ThreeLineMenu:
    def __init__(self, pos=(16, 72), size=(900, 400), alpha=200, font=None):
        self.x, self.y = pos
        self.w, self.h = size
        self.alpha = alpha
        self.font = font or pygame.font.SysFont("arial", 15)
        self.title_font = pygame.font.SysFont("arial", 18, bold=True)
        self.surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        self.character_info = []
        self.expanded = False
        self.btn_font = pygame.font.SysFont("arial", 22, bold=True)
        self.btn_width = 190
        self.btn_height = 48
        self.btn_bg = pygame.Surface((self.btn_width, self.btn_height), pygame.SRCALPHA)
        pygame.draw.rect(self.btn_bg, (40, 45, 52, 230), self.btn_bg.get_rect(), border_radius=10)
        pygame.draw.rect(self.btn_bg, (100, 200, 255, 255), self.btn_bg.get_rect(), 2, border_radius=10)
        line_color = (255, 255, 255)
        pygame.draw.rect(self.btn_bg, line_color, pygame.Rect(18, 10, 28, 4), border_radius=2)
        pygame.draw.rect(self.btn_bg, line_color, pygame.Rect(18, 19, 28, 4), border_radius=2)
        pygame.draw.rect(self.btn_bg, line_color, pygame.Rect(18, 28, 28, 4), border_radius=2)
        self.btn_text = self.btn_font.render("Asignaciones", True, (255, 255, 255))
        self.btn_rect = pygame.Rect(self.x, self.y, self.btn_width, self.btn_height)
        self.panel_rect = pygame.Rect(self.x, self.y + self.btn_height + 5, self.w, self.h)
        self.scroll_offset = 0
        self.scroll_speed = 25
        self.inner_height = 0

    def set_character_info(self, info):
        self.character_info = info
        self.inner_height = 55 + len(info) * 62

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = e.pos
            if self.btn_rect.collidepoint(mx, my):
                self.expanded = not self.expanded
                return True
            if self.expanded and not self.panel_rect.collidepoint(mx, my):
                self.expanded = False
                return True
        if self.expanded and e.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.panel_rect.collidepoint(mx, my):
                self.scroll_offset -= e.y * self.scroll_speed
                max_off = max(0, self.inner_height - self.h)
                if self.scroll_offset < 0:
                    self.scroll_offset = 0
                if self.scroll_offset > max_off:
                    self.scroll_offset = max_off
                return True
        return False

    def draw(self, surf):
        surf.blit(self.btn_bg, (self.x, self.y))
        surf.blit(self.btn_text, (self.x + 36, self.y + 10))
        if not self.expanded:
            return
        self.surface.fill((30, 35, 42, self.alpha))
        pygame.draw.rect(self.surface, (100, 200, 255, 255), self.surface.get_rect(), 3, border_radius=12)
        title = self.title_font.render("📋 Estado de Personajes", True, (100, 200, 255))
        self.surface.blit(title, (20, 15))
        pygame.draw.line(self.surface, (100, 200, 255, 180), (20, 48), (self.w - 20, 48), 2)
        clip_rect = pygame.Rect(0, 50, self.w, self.h - 55)
        old_clip = self.surface.get_clip()
        self.surface.set_clip(clip_rect)
        y = 55 - self.scroll_offset
        for info in self.character_info:
            t1 = self.font.render(f"{info['name']} ({info['type']})", True, (255, 255, 100))
            self.surface.blit(t1, (25, y))
            t2 = self.font.render(
                f" ❤️ {info['health']:.0f} | ⚡ {info['energia']:.0f} | {info['status']}",
                True, (210, 210, 210)
            )
            self.surface.blit(t2, (25, y + 20))
            t3 = self.font.render(f"Lvl {info['level']} | XP {info.get('xp',0)}", True, (150, 220, 255))
            self.surface.blit(t3, (25, y + 40))
            y += 62
        self.surface.set_clip(old_clip)
        surf.blit(self.surface, (self.x, self.y + self.btn_height + 5))


class State:
    def handle(self, e): ...
    def update(self, dt): ...
    def draw(self, surf): ...


class MainMenu(State):
    def __init__(self):
        self.manager = pygame_gui.UIManager((W, H))
        self.title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(W // 2 - 260, 80, 520, 60),
            text="Village Builder - Con Estructuras de Datos",
            manager=self.manager
        )
        self.btn_jugar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(W // 2 - 100, 200, 200, 48),
            text="Jugar",
            manager=self.manager
        )
        self.btn_nuevo = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(W // 2 - 100, 260, 200, 48),
            text="Juego nuevo",
            manager=self.manager
        )
        self.status = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(W // 2 - 280, 340, 560, 28),
            text="Selecciona una opción…",
            manager=self.manager
        )
        self.next_state = None

    def handle(self, e):
        if e.type == pygame.USEREVENT and e.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if e.ui_element == self.btn_jugar:
                self.next_state = Game(resume=True)
            elif e.ui_element == self.btn_nuevo:
                self.next_state = Game(resume=False)
        self.manager.process_events(e)

    def update(self, dt):
        self.manager.update(dt)

    def draw(self, surf):
        surf.fill(BG_COLOR)
        self.manager.draw_ui(surf)


class Game(State):
    def __init__(self, resume=False):
        self.manager = pygame_gui.UIManager((W, H))
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 13)
        self.resume = resume
        self.tiempo_actual = 0.0

        self.cofre_materiales = CofrePrincipal()
        self.cofre_materiales.inicializar_herramientas()
        self.cofre_comida = CofreAlimentos()
        self.bar = Bar()
        self.inv_mats = {"madera": 0, "piedra": 0}
        self.inv_food = {"leche": 0, "huevos": 0, "trigo": 0}

        self.gestor = GestorPoblacion()
        self.planificador = PlanificadorTareas(self)

        self.terminal = TerminalLogs()
        self.terminal.log("[00:00:00] ▸ Sistema iniciado")
        self.terminal.log("[00:00:00] ▸ Entrando a 'Village Builder'")

        self.selector = SelectorPersonajes(self.gestor)

        btn_w = 115
        btn_h = 36
        sep = 6
        total_w = 6 * btn_w + 5 * sep
        start_x = (W - total_w) // 2
        y1 = 8
        y2 = 8 + btn_h + 6

        self.btn_back = pygame_gui.elements.UIButton(pygame.Rect(10, 8, 110, 36), "← Volver", self.manager)
        self.btn_comer = pygame_gui.elements.UIButton(pygame.Rect(start_x + 0 * (btn_w + sep), y1, btn_w, btn_h), "🍽 COMER", self.manager)
        self.btn_minar = pygame_gui.elements.UIButton(pygame.Rect(start_x + 1 * (btn_w + sep), y1, btn_w, btn_h), "⛏ MINAR", self.manager)
        self.btn_talar = pygame_gui.elements.UIButton(pygame.Rect(start_x + 2 * (btn_w + sep), y1, btn_w, btn_h), "🪓 TALAR", self.manager)
        self.btn_construir = pygame_gui.elements.UIButton(pygame.Rect(start_x + 3 * (btn_w + sep), y1, btn_w, btn_h), "🏗 CONSTR.", self.manager)
        self.btn_ordeñar = pygame_gui.elements.UIButton(pygame.Rect(start_x + 4 * (btn_w + sep), y1, btn_w, btn_h), "🥛 ORDEÑAR", self.manager)
        self.btn_huevos = pygame_gui.elements.UIButton(pygame.Rect(start_x + 5 * (btn_w + sep), y1, btn_w, btn_h), "🥚 HUEVOS", self.manager)

        self.btn_bar = pygame_gui.elements.UIButton(pygame.Rect(start_x + 0 * (btn_w + sep), y2, btn_w, btn_h), "🍺 BAR", self.manager)
        self.btn_cosechar = pygame_gui.elements.UIButton(pygame.Rect(start_x + 1 * (btn_w + sep), y2, btn_w, btn_h), "🌾 COSECHAR", self.manager)
        self.btn_plantar = pygame_gui.elements.UIButton(pygame.Rect(start_x + 2 * (btn_w + sep), y2, btn_w, btn_h), "🌱 PLANTAR", self.manager)
        self.btn_chest_materials = pygame_gui.elements.UIButton(pygame.Rect(start_x + 3 * (btn_w + sep), y2, btn_w, btn_h), "📦 MATS", self.manager)
        self.btn_chest_food = pygame_gui.elements.UIButton(pygame.Rect(start_x + 4 * (btn_w + sep), y2, btn_w, btn_h), "🍖 COMIDA", self.manager)
        self.btn_stress = pygame_gui.elements.UIButton(pygame.Rect(start_x + 5 * (btn_w + sep), y2, btn_w, btn_h), "⚙ PRUEBA", self.manager)

        self.showing_build_menu = False
        self.build_menu_window = None
        self.showing_material_chest_menu = False
        self.material_chest_menu_window = None
        self.showing_food_chest_menu = False
        self.food_chest_menu_window = None
        self.showing_bar_menu = False
        self.bar_select_window = None
        self.bar_select_buttons = []

        self.load_expanded_map()
        self.camera = Camera(self.map_width, self.map_height, W, H)

        self.characters_visual = LinkedList()
        self.personaje_to_visual = {}

        margin = 140
        extra = 140
        self.walk_bounds = pygame.Rect(
            margin,
            margin,
            self.map_width - margin * 2 - extra,
            self.map_height - margin * 2 - extra
        )

        edge_margin = 150
        self.edge_zones = [
            pygame.Rect(0, 0, edge_margin, self.map_height),
            pygame.Rect(self.map_width - edge_margin, 0, edge_margin, self.map_height),
            pygame.Rect(0, 0, self.map_width, edge_margin),
            pygame.Rect(0, self.map_height - edge_margin, self.map_width, edge_margin)
        ]

        self.map_objects = LinkedList()
        self.animal_vel = {}
        self.animal_frozen = {}
        self.animal_thirst_timer = {}
        self.animal_thirst_interval = {}
        self.animal_going_to_drink = {}
        self.animal_drinking = {}
        self.animal_drinking_timer = {}
        self.animal_drinking_duration = 10.0

        self.load_map_objects()
        self.create_bar()
        self.create_water_trough()
        self.create_chests()
        self.create_game_characters()

        self.goblins = LinkedList()
        self.goblin_spawn_timer = 0.0
        self.goblin_spawn_interval = 45.0
        self.max_goblins = 4
        self.goblins_defeated = 0

        num_duendes_iniciales = random.randint(1, 2)
        i_du = 0
        while i_du < num_duendes_iniciales:
            self.spawn_goblin()
            i_du += 1

        self.menu3 = ThreeLineMenu(pos=(310, 110), size=(690, 360), alpha=210, font=self.small_font)
        self._sync_menu()

        self.lbl_mat_madera = None
        self.lbl_mat_piedra = None
        self.lbl_food_leche = None
        self.lbl_food_huevos = None
        self.lbl_food_trigo = None

        self.lbl_ultimo_seleccionado = pygame_gui.elements.UILabel(
            pygame.Rect(135, 52, 650, 18),
            "Selector inteligente listo",
            self.manager
        )
        self.terminal.log("[00:00:00] ▸ Juego iniciado correctamente")

        self.construcciones_pendientes = LinkedList()

    def create_game_characters(self):
        c1 = random.randint(1, 2)
        i = 0
        while i < c1:
            en = Enano(posicion=(700 + i * 50, 380 + i * 20))
            self.add_character_from_personaje(en, "enano.gif", 0.1, nombre_random=random.choice(NOMBRES_ENANOS))
            self.gestor.agregar_enano(en)
            self.terminal.log("• Enano " + str(i + 1) + " creado")
            i += 1

        c2 = random.randint(2, 3)
        i = 0
        while i < c2:
            m = Minero(posicion=(300 + i * 50, 400 + i * 20))
            self.add_character_from_personaje(m, "minero.gif", 0.4, nombre_random=random.choice(NOMBRES_MINEROS))
            self.gestor.agregar_enano(m)
            self.terminal.log("• Minero creado")
            i += 1

        c3 = random.randint(3, 4)
        i = 0
        while i < c3:
            g = Granjero(posicion=(600 + i * 50, 370 + i * 20))
            self.add_character_from_personaje(g, "granjero.gif", 0.3, nombre_random=random.choice(NOMBRES_GRANJEROS))
            self.gestor.agregar_enano(g)
            self.terminal.log("• Granjero creado")
            i += 1

        c4 = random.randint(2, 3)
        i = 0
        while i < c4:
            l = Lenador(posicion=(400 + i * 50, 350 + i * 20))
            self.add_character_from_personaje(l, "lenhador.gif", 0.2, nombre_random=random.choice(NOMBRES_LENADORES))
            self.gestor.agregar_enano(l)
            self.terminal.log("• Leñador creado")
            i += 1

        c5 = random.randint(1, 2)
        i = 0
        while i < c5:
            c = Constructor(posicion=(500 + i * 50, 360 + i * 20))
            self.add_character_from_personaje(c, "constructor.gif", 0.2, nombre_random=random.choice(NOMBRES_CONSTRUCTORES))
            self.gestor.agregar_enano(c)
            self.terminal.log("• Constructor creado")
            i += 1

    def add_character_from_personaje(self, personaje_obj, gif_path, scale, nombre_random="NPC"):
        frames = load_gif_frames(gif_path, scale)
        if not frames:
            surf = pygame.Surface((40, 50), pygame.SRCALPHA)
            pygame.draw.rect(surf, (100, 100, 200), surf.get_rect(), border_radius=5)
            frames = [surf]
        visual = {
            "personaje": personaje_obj,
            "frames": frames,
            "pos": list(personaje_obj.posicion),
            "frame_index": 0,
            "anim_timer": 0.0,
            "target": None,
            "target_obj": None,
            "moving": True,
            "visible": True,
            "going_to_chest": False,
            "pending_resource": None,
            "xp": 0,
            "display_name": nombre_random,
            "going_to_bar": False,
            "in_bar": False,
            "bar_timer": 0.0,
            "work_speed_mult": 1.0,
            "buff_until": 0.0,
            "goblin_cd": 0.0,
        }
        self.characters_visual.add(visual)
        self.personaje_to_visual[id(personaje_obj)] = visual

    def _sync_menu(self):
        info = []
        chars = to_list(self.characters_visual)
        total = length(self.characters_visual)
        i = 0
        while i < total:
            visual = chars[i]
            if not visual["visible"] and not visual.get("in_bar", False):
                i += 1
                continue
            p = visual["personaje"]
            if visual.get("in_bar", False):
                status = "En el bar"
            elif visual.get("going_to_bar", False):
                status = "Yendo al bar"
            elif p.accion_actual:
                status = "Trabajando: " + p.accion_actual.get("accion", "...")
            else:
                if visual.get("going_to_chest", False):
                    status = "Llevando al cofre"
                else:
                    status = "Libre"
            info.append({
                "type": p.tipo,
                "name": visual.get("display_name", p.simbolo),
                "level": p.nivel,
                "health": p.salud,
                "energia": p.energia,
                "status": status,
                "xp": visual.get("xp", 0)
            })
            i += 1
        self.menu3.set_character_info(info)

    def load_expanded_map(self):
        tile_surfaces = []
        tile_w = tile_h = 0
        j = 0
        while j < len(MAP_TILES):
            row = MAP_TILES[j]
            rs = []
            i = 0
            while i < len(row):
                path = row[i]
                try:
                    t = pygame.image.load(path).convert()
                    rs.append(t)
                    if tile_w == 0:
                        tile_w, tile_h = t.get_size()
                except Exception:
                    surf = pygame.Surface((W, H))
                    surf.fill((60, 110, 70))
                    rs.append(surf)
                    if tile_w == 0:
                        tile_w, tile_h = W, H
                i += 1
            tile_surfaces.append(rs)
            j += 1
        self.map_width = tile_w * len(MAP_TILES[0])
        self.map_height = tile_h * len(MAP_TILES)
        self.map_surface = pygame.Surface((self.map_width, self.map_height))
        j = 0
        while j < len(tile_surfaces):
            row = tile_surfaces[j]
            i = 0
            while i < len(row):
                t = row[i]
                self.map_surface.blit(t, (i * tile_w, j * tile_h))
                i += 1
            j += 1

    def get_distance_rules(self):
        return {
            ('piedra', 'piedra'): 5,
            ('casa', 'casa'): 150,
            ('casa', 'establo'): 150,
            ('arbol', 'arbol'): 25,
            ('vaca', 'vaca'): 60,
            ('gallina', 'gallina'): 25,
        }

    def load_map_objects(self):
        distance_rules = self.get_distance_rules()
        object_types = [
            {"path": "piedra.png", "type": "piedra", "scale": 0.10, "count": random.randint(18, 25)},
            {"path": "arbol.png", "type": "arbol", "scale": 0.10, "count": random.randint(18, 25)},
            {"path": "casa.png", "type": "casa", "scale": 0.20, "count": random.randint(1, 2)},
            {"path": "establo.png", "type": "establo", "scale": 0.15, "count": random.randint(1, 2)},
            {"path": "vaca.gif", "type": "vaca", "scale": 0.18, "count": random.randint(8, 12)},
            {"path": "gallina.gif", "type": "gallina", "scale": 0.14, "count": random.randint(8, 12)},
        ]
        margin = 100
        placed = []
        k = 0
        while k < len(object_types):
            od = object_types[k]
            try:
                if od["path"].endswith(".gif"):
                    frames = load_gif_frames(od["path"], od["scale"])
                    if frames:
                        base_img = frames[0]
                    else:
                        base_img = pygame.Surface((32, 32), pygame.SRCALPHA)
                else:
                    img = pygame.image.load(od["path"]).convert_alpha()
                    w, h = img.get_size()
                    base_img = pygame.transform.smoothscale(img, (int(w * od["scale"]), int(h * od["scale"])))
                img_rect = base_img.get_rect()

                if od["type"] in ("casa", "establo"):
                    extra_right = img_rect.width + 80
                    extra_bottom = img_rect.height + 80
                else:
                    extra_right = 80
                    extra_bottom = 80

                safe_x = (margin, self.map_width - extra_right)
                safe_y = (margin, self.map_height - extra_bottom)

                c = od["count"]
                ci = 0
                while ci < c:
                    pos, placed_rect = find_valid_position(
                        img_rect,
                        od["type"],
                        safe_x,
                        safe_y,
                        placed,
                        distance_rules
                    )
                    if placed_rect:
                        placed.append((placed_rect, od["type"]))

                    obj = {"image": base_img, "pos": list(pos), "type": od["type"]}
                    if od["path"].endswith(".gif"):
                        obj["frames"] = frames
                        obj["frame_index"] = 0

                    self.map_objects.add(obj)

                    if od["type"] in ("vaca", "gallina"):
                        oid = id(obj)
                        self.animal_vel[oid] = [random.uniform(-12, 12), random.uniform(-12, 12)]
                        self.animal_frozen[oid] = False
                        self.animal_thirst_timer[oid] = 0.0
                        self.animal_thirst_interval[oid] = random.uniform(15.0, 35.0)
                        self.animal_going_to_drink[oid] = False
                        self.animal_drinking[oid] = False
                        self.animal_drinking_timer[oid] = 0.0
                    ci += 1
            except Exception as e:
                print("[MAP_OBJ]", e)
            k += 1

    def create_bar(self):
        cx = self.map_width // 2
        cy = self.map_height // 2
        try:
            img = pygame.image.load("bar.png").convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * 0.25), int(h * 0.25)))
        except Exception:
            img = pygame.Surface((80, 70), pygame.SRCALPHA)
            pygame.draw.rect(img, (139, 69, 19), img.get_rect(), border_radius=8)
        self.bar_position = [float(cx - img.get_width() // 2), float(cy - img.get_height() // 2)]
        self.bar_obj = {"image": img, "pos": list(self.bar_position), "type": "bar"}
        self.map_objects.add(self.bar_obj)
        self.bar_exit_pos = [self.bar_position[0] + img.get_width() + 10, self.bar_position[1] + 5]

    def create_water_trough(self):
        establo = None
        objs = to_list(self.map_objects)
        n = length(self.map_objects)
        i = 0
        while i < n:
            if objs[i]["type"] == "establo":
                establo = objs[i]
                break
            i += 1
        if establo:
            ex, ey = establo["pos"]
            ew = establo["image"].get_width()
            tx = ex + ew + 20
            ty = ey + 10
        else:
            tx = 300
            ty = 200
        try:
            img = pygame.image.load("bebedero.png").convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * 0.05), int(h * 0.05)))
        except Exception:
            img = pygame.Surface((25, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(img, (100, 150, 200), pygame.Rect(1, 4, 23, 11))
        self.water_trough_position = [float(tx), float(ty)]
        self.map_objects.add({"image": img, "pos": list(self.water_trough_position), "type": "bebedero"})

    def create_chests(self):
        casa = None
        objs = to_list(self.map_objects)
        n = length(self.map_objects)
        i = 0
        while i < n:
            if objs[i]["type"] == "casa":
                casa = objs[i]
                break
            i += 1
        if casa:
            cx, cy = casa["pos"]
            cw = casa["image"].get_width()
            ch = casa["image"].get_height()
            mx = cx - 35
            my = cy + ch // 2 - 10
            fx = cx + cw + 10
            fy = cy + ch // 2 - 10
        else:
            mx, my = 200, 200
            fx, fy = 300, 200
        mat_frames = load_gif_frames("cofre.gif", 0.15)
        if not mat_frames:
            placeholder = pygame.Surface((40, 35), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (139, 90, 43), pygame.Rect(5, 10, 30, 20), border_radius=3)
            mat_frames = [placeholder]
        food_frames = load_gif_frames("cofre.gif", 0.15)
        if not food_frames:
            placeholder = pygame.Surface((40, 35), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (139, 90, 43), pygame.Rect(5, 10, 30, 20), border_radius=3)
            food_frames = [placeholder]
        self.material_chest_obj = {
            "frames": mat_frames,
            "image": mat_frames[0],
            "pos": [float(mx), float(my)],
            "type": "cofre_material",
            "frame_index": 0
        }
        self.map_objects.add(self.material_chest_obj)
        self.food_chest_obj = {
            "frames": food_frames,
            "image": food_frames[0],
            "pos": [float(fx), float(fy)],
            "type": "cofre_comida",
            "frame_index": 0
        }
        self.map_objects.add(self.food_chest_obj)

    def spawn_goblin(self):
        zone = random.choice(self.edge_zones)
        x = random.randint(zone.left, zone.right - 40)
        y = random.randint(zone.top, zone.bottom - 40)
        frames = load_gif_frames("duende.gif", 0.22)
        if not frames:
            s = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 150, 0), (20, 20), 15)
            frames = [s]
        gob = {
            "frames": frames,
            "pos": [float(x), float(y)],
            "frame_index": 0,
            "target": None,
            "state": "patrol",
            "health": 50,
            "attack_cooldown": 0.0,
            "attack_damage": 8,
            "detection_range": 200,
            "attack_range": 30,
            "is_attacking": False,
        }
        self.goblins.add(gob)
        self.terminal.log("• Duende apareció en el mapa")

    def start_task(self, task_type):
        self.planificador.registrar_evento(
            TipoEvento.ORDEN_USUARIO,
            {'accion': task_type, 'parametros': {}}
        )
        self.planificador.procesar_buffer()
        tarea = self.planificador.obtener_siguiente_tarea()
        if not tarea:
            self.terminal.log(f"⚠ No se pudo crear tarea: {task_type}")
            return

        mejor_personaje = None

        if seleccionar_personaje_inteligente is not None:
            mejor_personaje = seleccionar_personaje_inteligente(self.gestor, task_type)

        if mejor_personaje is None:
            if hasattr(self.gestor, "obtener_personaje_disponible"):
                mejor_personaje = self.gestor.obtener_personaje_disponible(task_type)
            else:
                self.terminal.log(f"⚠ No hay personajes disponibles para '{task_type}' (gestor sin método)")
                self.lbl_ultimo_seleccionado.set_text(f"⚠ No hay personajes disponibles para {task_type}")
                return

        if mejor_personaje is None:
            self.terminal.log(f"⚠ No hay personajes disponibles para '{task_type}'")
            self.lbl_ultimo_seleccionado.set_text(f"⚠ No hay personajes disponibles para {task_type}")
            return

        visual_seleccionado = None
        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        while i < n:
            if chars[i]["personaje"] == mejor_personaje:
                visual_seleccionado = chars[i]
                break
            i += 1

        if visual_seleccionado:
            self._assign_task_to_visual(visual_seleccionado, tarea)
            nombre = visual_seleccionado.get("display_name", "NPC")
            msg = f"✅ {nombre} → {task_type}"
            self.lbl_ultimo_seleccionado.set_text(msg)
            self.terminal.log(msg)
        else:
            self.terminal.log("⚠ Error: no se encontró el visual")

    def _assign_task_to_visual(self, visual, tarea):
        p = visual["personaje"]
        p.asignar_accion(tarea)
        objs = to_list(self.map_objects)
        on = length(self.map_objects)
        if tarea['accion'] == 'minar':
            i = 0
            while i < on:
                if objs[i]["type"] == "piedra":
                    visual["target_obj"] = objs[i]
                    break
                i += 1
        elif tarea['accion'] == 'talar':
            i = 0
            while i < on:
                if objs[i]["type"] == "arbol":
                    visual["target_obj"] = objs[i]
                    break
                i += 1
        elif tarea['accion'] == 'ordeñar':
            i = 0
            while i < on:
                if objs[i]["type"] == "vaca":
                    visual["target_obj"] = objs[i]
                    break
                i += 1
        elif tarea['accion'] == 'huevos':
            i = 0
            while i < on:
                if objs[i]["type"] == "gallina":
                    visual["target_obj"] = objs[i]
                    break
                i += 1
        elif tarea['accion'] == 'comer':
            visual["target_obj"] = self.food_chest_obj
        elif tarea['accion'] == 'cosechar':
            i = 0
            while i < on:
                if objs[i]["type"] == "trigo_sembrado":
                    visual["target_obj"] = objs[i]
                    break
                i += 1

    def show_build_menu(self):
        if self.showing_build_menu:
            return
        self.showing_build_menu = True
        w_win, h_win = 400, 250
        x = (W - w_win) // 2
        y = (H - h_win) // 2
        self.build_menu_window = pygame_gui.elements.UIWindow(
            pygame.Rect(x, y, w_win, h_win),
            self.manager,
            window_display_title="¿Qué deseas construir?"
        )
        self.btn_build_casa = pygame_gui.elements.UIButton(
            pygame.Rect(50, 60, 300, 50),
            "🏠 Construir Casa (2🪵 + 1🪨)",
            self.manager,
            container=self.build_menu_window
        )
        self.btn_build_establo = pygame_gui.elements.UIButton(
            pygame.Rect(50, 120, 300, 50),
            "🐄 Construir Establo (2🪵 + 1🪨)",
            self.manager,
            container=self.build_menu_window
        )
        self.btn_build_cancel = pygame_gui.elements.UIButton(
            pygame.Rect(50, 180, 300, 40),
            "❌ Cancelar",
            self.manager,
            container=self.build_menu_window
        )

    def close_build_menu(self):
        if self.build_menu_window:
            self.build_menu_window.kill()
            self.build_menu_window = None
        self.showing_build_menu = False

    def show_material_chest_menu(self):
        if self.showing_material_chest_menu:
            return
        self.showing_material_chest_menu = True
        w_win, h_win = 350, 220
        x = (W - w_win) // 2
        y = (H - h_win) // 2
        self.material_chest_menu_window = pygame_gui.elements.UIWindow(
            pygame.Rect(x, y, w_win, h_win),
            self.manager,
            window_display_title="📦 Cofre de Materiales"
        )
        pygame_gui.elements.UILabel(pygame.Rect(20, 50, 310, 30), "=== INVENTARIO DE MATERIALES ===", self.manager, container=self.material_chest_menu_window)
        self.lbl_mat_madera = pygame_gui.elements.UILabel(
            pygame.Rect(40, 90, 270, 30),
            "🪵 Madera: " + str(self.inv_mats["madera"]),
            self.manager,
            container=self.material_chest_menu_window
        )
        self.lbl_mat_piedra = pygame_gui.elements.UILabel(
            pygame.Rect(40, 120, 270, 30),
            "🪨 Piedra: " + str(self.inv_mats["piedra"]),
            self.manager,
            container=self.material_chest_menu_window
        )
        self.btn_close_material_chest = pygame_gui.elements.UIButton(
            pygame.Rect(100, 160, 150, 40), "✅ Cerrar", self.manager, container=self.material_chest_menu_window
        )

    def close_material_chest_menu(self):
        if self.material_chest_menu_window:
            self.material_chest_menu_window.kill()
            self.material_chest_menu_window = None
        self.showing_material_chest_menu = False
        self.lbl_mat_madera = None
        self.lbl_mat_piedra = None

    def show_food_chest_menu(self):
        if self.showing_food_chest_menu:
            return
        self.showing_food_chest_menu = True
        w_win, h_win = 350, 260
        x = (W - w_win) // 2
        y = (H - h_win) // 2
        self.food_chest_menu_window = pygame_gui.elements.UIWindow(
            pygame.Rect(x, y, w_win, h_win),
            self.manager,
            window_display_title="🍖 Cofre de Comida"
        )
        pygame_gui.elements.UILabel(pygame.Rect(20, 50, 310, 30), "=== INVENTARIO DE ALIMENTOS ===", self.manager, container=self.food_chest_menu_window)
        self.lbl_food_leche = pygame_gui.elements.UILabel(
            pygame.Rect(40, 90, 270, 30),
            "🥛 Leche: " + str(self.inv_food["leche"]),
            self.manager,
            container=self.food_chest_menu_window
        )
        self.lbl_food_huevos = pygame_gui.elements.UILabel(
            pygame.Rect(40, 120, 270, 30),
            "🥚 Huevos: " + str(self.inv_food["huevos"]),
            self.manager,
            container=self.food_chest_menu_window
        )
        self.lbl_food_trigo = pygame_gui.elements.UILabel(
            pygame.Rect(40, 150, 270, 30),
            "🌾 Trigo: " + str(self.inv_food["trigo"]),
            self.manager,
            container=self.food_chest_menu_window
        )
        self.btn_close_food_chest = pygame_gui.elements.UIButton(
            pygame.Rect(100, 190, 150, 40), "✅ Cerrar", self.manager, container=self.food_chest_menu_window
        )

    def close_food_chest_menu(self):
        if self.food_chest_menu_window:
            self.food_chest_menu_window.kill()
            self.food_chest_menu_window = None
        self.showing_food_chest_menu = False
        self.lbl_food_leche = None
        self.lbl_food_huevos = None
        self.lbl_food_trigo = None

    def show_bar_select_menu(self):
        if self.bar_select_window:
            return
        w_win, h_win = 320, 340
        x = (W - w_win) // 2
        y = (H - h_win) // 2
        self.bar_select_window = pygame_gui.elements.UIWindow(
            pygame.Rect(x, y, w_win, h_win),
            self.manager,
            window_display_title="¿Quién va al bar?"
        )
        self.bar_select_buttons = []
        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        y_btn = 50
        i = 0
        while i < n:
            visual = chars[i]
            if not visual["visible"]:
                if not visual.get("in_bar", False):
                    i += 1
                    continue
            name = visual.get("display_name", "NPC")
            b = pygame_gui.elements.UIButton(
                pygame.Rect(20, y_btn, 260, 30),
                name,
                self.manager,
                container=self.bar_select_window
            )
            b._target_visual = visual
            self.bar_select_buttons.append(b)
            y_btn += 36
            i += 1
        self.bar_select_close = pygame_gui.elements.UIButton(
            pygame.Rect(80, h_win - 60, 160, 30),
            "Cerrar",
            self.manager,
            container=self.bar_select_window
        )

    def close_bar_select_menu(self):
        if self.bar_select_window:
            self.bar_select_window.kill()
            self.bar_select_window = None
        self.bar_select_buttons = []

    def send_visual_to_bar(self, visual):
        pj = visual["personaje"]
        pj.accion_actual = None
        visual["pending_resource"] = None
        visual["going_to_chest"] = False
        visual["target_obj"] = self.bar_obj
        visual["going_to_bar"] = True
        visual["in_bar"] = False
        visual["bar_timer"] = 0.0
        self.terminal.log("• " + visual.get("display_name", "NPC") + " va al bar")

    def _refresh_chest_labels(self):
        if self.showing_material_chest_menu:
            if self.lbl_mat_madera is not None:
                self.lbl_mat_madera.set_text("🪵 Madera: " + str(self.inv_mats["madera"]))
            if self.lbl_mat_piedra is not None:
                self.lbl_mat_piedra.set_text("🪨 Piedra: " + str(self.inv_mats["piedra"]))
        if self.showing_food_chest_menu:
            if self.lbl_food_leche is not None:
                self.lbl_food_leche.set_text("🥛 Leche: " + str(self.inv_food["leche"]))
            if self.lbl_food_huevos is not None:
                self.lbl_food_huevos.set_text("🥚 Huevos: " + str(self.inv_food["huevos"]))
            if self.lbl_food_trigo is not None:
                self.lbl_food_trigo.set_text("🌾 Trigo: " + str(self.inv_food["trigo"]))

    def crear_trigo_sembrado(self, x, y):
        try:
            img = pygame.image.load("trigo.png").convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * 0.25), int(h * 0.25)))
        except Exception:
            img = pygame.Surface((20, 28), pygame.SRCALPHA)
            pygame.draw.rect(img, (200, 180, 50), img.get_rect(), border_radius=3)
        obj = {"image": img, "pos": [float(x), float(y)], "type": "trigo_sembrado"}
        self.map_objects.add(obj)

    def _remove_map_object(self, target):
        nueva = LinkedList()
        objs = to_list(self.map_objects)
        n = length(self.map_objects)
        i = 0
        while i < n:
            o = objs[i]
            if o is not target:
                nueva.add(o)
            i += 1
        self.map_objects = nueva

    def _deposit_from_visual(self, visual, pj):
        pend = visual.get("pending_resource")
        if not pend:
            return
        recurso = pend["recurso"]
        cant = pend["cantidad"]
        if recurso == "piedra":
            self.inv_mats["piedra"] = self.inv_mats["piedra"] + cant
            try:
                self.cofre_materiales.guardar("piedra", cant)
            except Exception:
                pass
        elif recurso == "madera":
            self.inv_mats["madera"] = self.inv_mats["madera"] + cant
            try:
                self.cofre_materiales.guardar("madera", cant)
            except Exception:
                pass
        elif recurso in ("leche", "huevos", "trigo"):
            self.inv_food[recurso] = self.inv_food[recurso] + cant
            try:
                self.cofre_comida.guardar_comida(recurso, cant)
            except Exception:
                pass
        visual["pending_resource"] = None
        self._refresh_chest_labels()
        self._add_xp_to_visual(visual, pj, accion="depositar")
        visual["going_to_chest"] = False
        pj.accion_actual = None
        visual["moving"] = True
        visual["target"] = None
        visual["frame_index"] = 0
        self.terminal.log("• Depósito: +" + str(cant) + " " + recurso)

    def _add_xp_to_visual(self, visual, pj, accion="generica"):
        base_xp = 10
        if accion == "minar" or accion == "talar":
            base_xp = 12
        elif accion == "ordeñar" or accion == "huevos" or accion == "cosechar":
            base_xp = 10
        elif accion == "plantar":
            base_xp = 6
        elif accion == "depositar":
            base_xp = 4
        old_xp = visual.get("xp", 0)
        new_xp = old_xp + base_xp
        visual["xp"] = new_xp
        needed = 30 * pj.nivel
        if new_xp >= needed:
            pj.nivel = pj.nivel + 1
            visual["xp"] = 0
            self.terminal.log("• " + visual.get("display_name", "NPC") + " subió a Nv." + str(pj.nivel))

    def move_visual_towards(self, visual, tx, ty, dt, speed=65, stop_dist=20):
        x, y = visual["pos"]
        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy)
        if dist < stop_dist:
            return True
        dx /= dist
        dy /= dist
        visual["pos"][0] += dx * speed * dt
        visual["pos"][1] += dy * speed * dt
        return False

    def move_visual_towards_obj(self, obj, tx, ty, dt, speed=25, stop_dist=25):
        x, y = obj["pos"]
        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy)
        if dist < stop_dist:
            return True
        dx /= dist
        dy /= dist
        obj["pos"][0] += dx * speed * dt
        obj["pos"][1] += dy * speed * dt
        return False

    def _update_animals(self, dt):
        if not hasattr(self, "water_trough_position"):
            return
        wt_x, wt_y = self.water_trough_position
        objs = to_list(self.map_objects)
        n = length(self.map_objects)
        i = 0
        while i < n:
            obj = objs[i]
            if obj["type"] != "vaca" and obj["type"] != "gallina":
                i += 1
                continue
            oid = id(obj)
            if self.animal_drinking.get(oid, False):
                self.animal_drinking_timer[oid] -= dt
                if self.animal_drinking_timer[oid] <= 0:
                    self.animal_drinking[oid] = False
                    self.animal_going_to_drink[oid] = False
                i += 1
                continue
            self.animal_thirst_timer[oid] += dt
            if self.animal_thirst_timer[oid] >= self.animal_thirst_interval[oid]:
                self.animal_going_to_drink[oid] = True
            if self.animal_going_to_drink[oid]:
                arrived = self.move_visual_towards_obj(obj, wt_x, wt_y, dt, speed=25, stop_dist=25)
                if arrived:
                    self.animal_drinking[oid] = True
                    self.animal_drinking_timer[oid] = 4.0
                    self.animal_thirst_timer[oid] = 0.0
                    self.animal_thirst_interval[oid] = random.uniform(15.0, 35.0)
                i += 1
                continue
            vx, vy = self.animal_vel[oid]
            obj["pos"][0] += vx * dt
            obj["pos"][1] += vy * dt
            pad = 80
            if obj["pos"][0] < pad or obj["pos"][0] > self.map_width - pad:
                self.animal_vel[oid][0] *= -1
            if obj["pos"][1] < pad or obj["pos"][1] > self.map_height - pad:
                self.animal_vel[oid][1] *= -1
            if random.random() < 0.005:
                self.animal_vel[oid][0] = random.uniform(-15, 15)
                self.animal_vel[oid][1] = random.uniform(-15, 15)
            i += 1

    def _hay_alguien_comiendo(self):
        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        while i < n:
            visual = chars[i]
            pj = visual["personaje"]
            if pj.accion_actual is not None:
                acc = pj.accion_actual.get("accion")
                if acc == "comer":
                    return True
            i += 1
        return False

    def _visual_menor_vida_para_comer(self):
        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        elegido = None
        while i < n:
            visual = chars[i]
            pj = visual["personaje"]
            puede = True
            if pj.salud >= 100:
                puede = False
            if pj.salud <= 0:
                puede = False
            if pj.accion_actual is not None:
                puede = False
            if visual.get("going_to_chest", False):
                puede = False
            if visual.get("going_to_bar", False):
                puede = False
            if visual.get("in_bar", False):
                puede = False
            if puede:
                if elegido is None:
                    elegido = visual
                else:
                    if pj.salud < elegido["personaje"].salud:
                        elegido = visual
            i += 1
        return elegido

    def iniciar_construccion(self, tipo_edificio):
        if self.inv_mats["madera"] < 2 or self.inv_mats["piedra"] < 1:
            self.terminal.log(f"⚠ No hay materiales suficientes para {tipo_edificio}")
            return
        
        mejor_personaje = None
        if seleccionar_personaje_inteligente is not None:
            mejor_personaje = seleccionar_personaje_inteligente(self.gestor, "construir")
        
        if mejor_personaje is None:
            if hasattr(self.gestor, "obtener_personaje_disponible"):
                mejor_personaje = self.gestor.obtener_personaje_disponible("construir")
        
        if mejor_personaje is None:
            self.terminal.log(f"⚠ No hay constructores disponibles")
            return
        
        visual_constructor = None
        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        while i < n:
            if chars[i]["personaje"] == mejor_personaje:
                visual_constructor = chars[i]
                break
            i += 1
        
        if visual_constructor is None:
            return
        
        self.inv_mats["madera"] -= 2
        self.inv_mats["piedra"] -= 1
        self._refresh_chest_labels()
        
        margin = 100
        x = random.randint(margin, self.map_width - margin - 150)
        y = random.randint(margin, self.map_height - margin - 150)
        
        construccion = {
            "tipo": tipo_edificio,
            "constructor_visual": visual_constructor,
            "posicion": [float(x), float(y)]
        }
        self.construcciones_pendientes.add(construccion)
        
        tarea = {"accion": "construir", "parametros": {"tipo": tipo_edificio}}
        mejor_personaje.asignar_accion(tarea)
        visual_constructor["target_obj"] = None
        visual_constructor["construccion_pos"] = construccion["posicion"]
        
        self.terminal.log(f"✅ {visual_constructor.get('display_name', 'Constructor')} iniciará construcción de {tipo_edificio}")

    def finalizar_construccion(self):
        if length(self.construcciones_pendientes) == 0:
            return
        
        lista_temp = to_list(self.construcciones_pendientes)
        construccion = lista_temp[0]
        
        nueva_lista = LinkedList()
        i = 1
        while i < len(lista_temp):
            nueva_lista.add(lista_temp[i])
            i += 1
        self.construcciones_pendientes = nueva_lista
        
        tipo = construccion["tipo"]
        pos = construccion["posicion"]
        
        if tipo == "casa":
            try:
                img = pygame.image.load("casa.png").convert_alpha()
                w, h = img.get_size()
                img = pygame.transform.smoothscale(img, (int(w * 0.20), int(h * 0.20)))
            except Exception:
                img = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.rect(img, (180, 140, 100), img.get_rect(), border_radius=8)
        else:
            try:
                img = pygame.image.load("establo.png").convert_alpha()
                w, h = img.get_size()
                img = pygame.transform.smoothscale(img, (int(w * 0.15), int(h * 0.15)))
            except Exception:
                img = pygame.Surface((70, 70), pygame.SRCALPHA)
                pygame.draw.rect(img, (139, 90, 43), img.get_rect(), border_radius=8)
        
        nuevo_edificio = {
            "image": img,
            "pos": pos,
            "type": tipo
        }
        self.map_objects.add(nuevo_edificio)
        
        self.terminal.log(f"🏗 {tipo.capitalize()} construida exitosamente")

    def handle(self, e):
        global current_state
        if self.menu3.handle(e):
            return
        if self.terminal.handle(e):
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if self.showing_build_menu:
                    self.close_build_menu()
                    return
                if self.showing_material_chest_menu:
                    self.close_material_chest_menu()
                    return
                if self.showing_food_chest_menu:
                    self.close_food_chest_menu()
                    return
                if self.bar_select_window:
                    self.close_bar_select_menu()
                    return
                current_state = MainMenu()
            elif e.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                self.camera.zoom_in()
            elif e.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.camera.zoom_out()
            elif e.key == pygame.K_F9:
                self.terminal.log("▶ Ejecutando PRUEBA DE ESTRÉS (F9)…")
                ejecutar_prueba_estres(self)
                return

        if e.type == pygame.USEREVENT and e.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if e.ui_element == self.btn_back:
                current_state = MainMenu()
            elif e.ui_element == self.btn_comer:
                self.start_task("comer")
            elif e.ui_element == self.btn_minar:
                self.start_task("minar")
            elif e.ui_element == self.btn_talar:
                self.start_task("talar")
            elif e.ui_element == self.btn_construir:
                self.show_build_menu()
            elif e.ui_element == self.btn_ordeñar:
                self.start_task("ordeñar")
            elif e.ui_element == self.btn_huevos:
                self.start_task("huevos")
            elif e.ui_element == self.btn_plantar:
                self.start_task("plantar")
            elif e.ui_element == self.btn_cosechar:
                self.start_task("cosechar")
            elif e.ui_element == self.btn_chest_materials:
                self.show_material_chest_menu()
            elif e.ui_element == self.btn_chest_food:
                self.show_food_chest_menu()
            elif e.ui_element == self.btn_bar:
                self.show_bar_select_menu()
            elif e.ui_element == self.btn_stress:
                self.terminal.log("▶ Ejecutando PRUEBA DE ESTRÉS (botón)…")
                ejecutar_prueba_estres(self)

            if self.bar_select_window:
                if e.ui_element == self.bar_select_close:
                    self.close_bar_select_menu()
                else:
                    i = 0
                    while i < len(self.bar_select_buttons):
                        b = self.bar_select_buttons[i]
                        if e.ui_element == b:
                            visual = getattr(b, "_target_visual", None)
                            if visual is not None:
                                self.send_visual_to_bar(visual)
                            self.close_bar_select_menu()
                            break
                        i += 1

            if self.showing_build_menu and self.build_menu_window:
                if hasattr(self, 'btn_build_casa') and e.ui_element == self.btn_build_casa:
                    self.iniciar_construccion("casa")
                    self.close_build_menu()
                elif hasattr(self, 'btn_build_establo') and e.ui_element == self.btn_build_establo:
                    self.iniciar_construccion("establo")
                    self.close_build_menu()
                elif hasattr(self, 'btn_build_cancel') and e.ui_element == self.btn_build_cancel:
                    self.close_build_menu()

            if self.showing_material_chest_menu and hasattr(self, 'btn_close_material_chest'):
                if e.ui_element == self.btn_close_material_chest:
                    self.close_material_chest_menu()
            if self.showing_food_chest_menu and hasattr(self, 'btn_close_food_chest'):
                if e.ui_element == self.btn_close_food_chest:
                    self.close_food_chest_menu()

        self.manager.process_events(e)

    def update(self, dt):
        self.manager.update(dt)
        self.tiempo_actual += dt

        keys = pygame.key.get_pressed()
        self.camera.update(dt, keys)

        self.gestor.actualizar_poblacion()

        if not self._hay_alguien_comiendo():
            if (self.inv_food["trigo"] > 0) or (self.inv_food["leche"] > 0) or (self.inv_food["huevos"] > 0):
                candidato = self._visual_menor_vida_para_comer()
                if candidato is not None:
                    pj_c = candidato["personaje"]
                    if pj_c.salud < 100:
                        pj_c.asignar_accion({"accion": "comer", "parametros": {}})
                        candidato["target_obj"] = self.food_chest_obj
                        candidato["going_to_chest"] = False
                        self.terminal.log("• " + candidato.get('display_name', 'NPC') + " va a comer (menos vida)")

        self.goblin_spawn_timer += dt
        if self.goblin_spawn_timer >= self.goblin_spawn_interval:
            count_alive = 0
            for g in to_list(self.goblins):
                if g["health"] > 0:
                    count_alive += 1
            if count_alive < self.max_goblins:
                self.spawn_goblin()
            self.goblin_spawn_timer = 0.0

        for gob in to_list(self.goblins):
            self.update_goblin_ai(gob, dt)

        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        while i < n:
            visual = chars[i]
            pj = visual["personaje"]

            if visual["work_speed_mult"] > 1.0 and self.tiempo_actual > visual["buff_until"]:
                visual["work_speed_mult"] = 1.0

            if visual.get("in_bar", False):
                visual["bar_timer"] -= dt
                if visual["bar_timer"] <= 0:
                    visual["in_bar"] = False
                    visual["visible"] = True
                    visual["pos"][0] = self.bar_exit_pos[0]
                    visual["pos"][1] = self.bar_exit_pos[1]
                    visual["work_speed_mult"] = 2.0
                    visual["buff_until"] = self.tiempo_actual + 180.0
                    visual["moving"] = True
                    visual["target"] = None
                i += 1
                continue

            if visual.get("going_to_bar", False):
                arrived = self.move_visual_towards(
                    visual,
                    self.bar_obj["pos"][0],
                    self.bar_obj["pos"][1],
                    dt,
                    speed=70,
                    stop_dist=40
                )
                if arrived:
                    visual["going_to_bar"] = False
                    visual["in_bar"] = True
                    visual["bar_timer"] = 5.0
                    visual["visible"] = False
                i += 1
                continue

            if not visual["visible"]:
                i += 1
                continue

            if pj.salud <= 0:
                i += 1
                continue

            visual["goblin_cd"] = max(0.0, visual.get("goblin_cd", 0.0) - dt)

            if getattr(pj, "tipo", "").lower() == "enano":
                en_x, en_y = character_anchor(visual)
                target_goblin = None
                min_d = 70
                for gob in to_list(self.goblins):
                    if gob["health"] <= 0:
                        continue
                    gx, gy = gob["pos"]
                    d = math.hypot(gx - en_x, gy - en_y)
                    if d < min_d:
                        min_d = d
                        target_goblin = gob
                if target_goblin is not None and visual["goblin_cd"] <= 0.0:
                    base_damage = 12 + 4 * (pj.nivel - 1)
                    cd = 1.1 - 0.05 * (pj.nivel - 1)
                    if cd < 0.3:
                        cd = 0.3
                    target_goblin["health"] -= base_damage
                    visual["goblin_cd"] = cd
                    self.terminal.log("⚔ " + visual.get('display_name', 'Enano') + " pegó al duende (-" + str(int(base_damage)) + ")")
                    if target_goblin["health"] <= 0:
                        self.goblins_defeated += 1
                        self.terminal.log("💀 Duende derrotado por un enano")

            visual["anim_timer"] += dt

            trabajando = (pj.accion_actual is not None) or visual.get("going_to_chest", False)
            if trabajando:
                accion_actual = pj.accion_actual.get("accion") if pj.accion_actual else None
                
                if accion_actual == "construir" and hasattr(visual, "construccion_pos"):
                    arrived = self.move_visual_towards(
                        visual,
                        visual["construccion_pos"][0],
                        visual["construccion_pos"][1],
                        dt,
                        speed=70,
                        stop_dist=30
                    )
                    visual["frame_index"] = 0
                    if not arrived:
                        i += 1
                        continue
                
                tgt = visual.get("target_obj", None)
                if tgt is not None:
                    if visual.get("going_to_chest", False):
                        arrived = self.move_visual_towards(
                            visual,
                            tgt["pos"][0],
                            tgt["pos"][1],
                            dt,
                            speed=70,
                            stop_dist=48
                        )
                    else:
                        arrived = self.move_visual_towards(
                            visual,
                            tgt["pos"][0],
                            tgt["pos"][1],
                            dt,
                            speed=70,
                            stop_dist=28
                        )
                    visual["frame_index"] = 0
                    if arrived:
                        if visual.get("going_to_chest", False):
                            self._deposit_from_visual(visual, pj)
                        else:
                            visual["target_obj"] = None
                            visual["anim_timer"] = 0.0
                    else:
                        if visual.get("going_to_chest", False):
                            dx = tgt["pos"][0] - visual["pos"][0]
                            dy = tgt["pos"][1] - visual["pos"][1]
                            dist = math.hypot(dx, dy)
                            if dist < 55:
                                self._deposit_from_visual(visual, pj)
                    i += 1
                    continue

                speed_mult = visual.get("work_speed_mult", 1.0)
                level_bonus = 1.0 + 0.12 * (pj.nivel - 1)
                if level_bonus < 0.4:
                    level_bonus = 0.4
                pj.tiempo_ocupado -= dt * speed_mult * level_bonus

                if visual["anim_timer"] >= 0.12:
                    visual["anim_timer"] = 0.0
                    frames = visual["frames"]
                    if frames:
                        visual["frame_index"] = (visual.get("frame_index", 0) + 1) % len(frames)
                if pj.tiempo_ocupado <= 0:
                    accion_name = None
                    if pj.accion_actual:
                        accion_name = pj.accion_actual.get("accion")
                    res = pj.completar_accion()

                    if accion_name == "construir":
                        self.finalizar_construccion()
                        self._add_xp_to_visual(visual, pj, accion="construir")
                        pj.accion_actual = None
                        visual["target_obj"] = None
                        visual["going_to_chest"] = False
                        visual["pending_resource"] = None
                        visual["moving"] = True
                        visual["target"] = None
                        visual["frame_index"] = 0
                        if hasattr(visual, "construccion_pos"):
                            delattr(visual, "construccion_pos")
                        i += 1
                        continue

                    if accion_name == "comer":
                        consumio = False
                        if self.inv_food["trigo"] > 0:
                            self.inv_food["trigo"] = self.inv_food["trigo"] - 1
                            consumio = True
                        elif self.inv_food["leche"] > 0:
                            self.inv_food["leche"] = self.inv_food["leche"] - 1
                            consumio = True
                        elif self.inv_food["huevos"] > 0:
                            self.inv_food["huevos"] = self.inv_food["huevos"] - 1
                            consumio = True

                        if consumio:
                            pj.salud = 100
                            self._refresh_chest_labels()
                            self.terminal.log("• " + visual.get('display_name', 'NPC') + " comió (+vida completa)")
                        else:
                            self.terminal.log("⚠ Quiso comer pero no había comida")

                        pj.accion_actual = None
                        visual["target_obj"] = None
                        visual["going_to_chest"] = False
                        visual["pending_resource"] = None
                        visual["moving"] = True
                        visual["target"] = None
                        visual["frame_index"] = 0
                        self._add_xp_to_visual(visual, pj, accion="comer")
                        i += 1
                        continue

                    if accion_name == "plantar":
                        gx, gy = visual["pos"]
                        self.crear_trigo_sembrado(gx, gy + 25)
                        self._add_xp_to_visual(visual, pj, accion="plantar")
                        pj.accion_actual = None
                        visual["target_obj"] = None
                        visual["going_to_chest"] = False
                        visual["pending_resource"] = None
                        visual["moving"] = True
                        visual["target"] = None
                        visual["frame_index"] = 0
                        i += 1
                        continue

                    recurso = None
                    cant = 1
                    if res and ("recurso" in res):
                        recurso = res["recurso"]
                        if "cantidad" in res:
                            cant = res["cantidad"]
                    else:
                        if accion_name == "minar":
                            recurso = "piedra"
                        elif accion_name == "talar":
                            recurso = "madera"
                        elif accion_name == "ordeñar":
                            recurso = "leche"
                        elif accion_name == "huevos":
                            recurso = "huevos"
                        elif accion_name == "cosechar":
                            recurso = "trigo"
                            tgt = visual.get("target_obj")
                            if tgt is not None and tgt.get("type") == "trigo_sembrado":
                                self._remove_map_object(tgt)

                    self._add_xp_to_visual(visual, pj, accion=accion_name or "generica")

                    if recurso is not None:
                        visual["pending_resource"] = {"recurso": recurso, "cantidad": cant}
                        if recurso == "piedra" or recurso == "madera":
                            visual["target_obj"] = self.material_chest_obj
                            visual["going_to_chest"] = True
                        else:
                            visual["target_obj"] = self.food_chest_obj
                            visual["going_to_chest"] = True

                    visual["frame_index"] = 0
            else:
                if visual["moving"]:
                    if visual["target"] is None:
                        x = random.randint(self.walk_bounds.left, self.walk_bounds.right)
                        y = random.randint(self.walk_bounds.top, self.walk_bounds.bottom)
                        visual["target"] = [float(x), float(y)]
                    else:
                        arrived = self.move_visual_towards(
                            visual,
                            visual["target"][0],
                            visual["target"][1],
                            dt,
                            speed=60,
                            stop_dist=20
                        )
                        visual["frame_index"] = 0
                        if arrived:
                            visual["target"] = None
                else:
                    visual["frame_index"] = 0
            i += 1

        self._update_animals(dt)

        self._sync_menu()

        gobs = to_list(self.goblins)
        ng = length(self.goblins)
        ig = 0
        while ig < ng:
            gob = gobs[ig]
            gob["frame_index"] = (gob.get("frame_index", 0) + 1) % len(gob["frames"])
            ig += 1

    def update_goblin_ai(self, goblin, dt):
        if goblin["health"] <= 0:
            return
        gob_x, gob_y = goblin["pos"]

        if goblin.get("target") and any(visual is goblin["target"] for visual in to_list(self.characters_visual)):
            target_visual = goblin["target"]
            pj = target_visual["personaje"]
            if pj.salud <= 0:
                goblin["target"] = None
                goblin["state"] = "patrol"
            else:
                tx, ty = character_anchor(target_visual)
                dx = tx - gob_x
                dy = ty - gob_y
                dist = math.hypot(dx, dy)
                if dist > goblin["attack_range"]:
                    dx /= dist
                    dy /= dist
                    goblin["pos"][0] += dx * 35 * dt
                    goblin["pos"][1] += dy * 35 * dt
                else:
                    goblin["attack_cooldown"] -= dt
                    if goblin["attack_cooldown"] <= 0:
                        pj.recibir_lesion("ataque de duende")
                        goblin["attack_cooldown"] = 3.5
                        if pj.salud <= 0:
                            target_visual["visible"] = False
                            goblin["target"] = None
                            goblin["state"] = "patrol"
            return

        nearest = None
        min_d = 999999
        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        while i < n:
            visual = chars[i]
            if visual["personaje"].salud <= 0:
                i += 1
                continue
            vx, vy = character_anchor(visual)
            d = math.hypot(vx - gob_x, vy - gob_y)
            if d < min_d:
                min_d = d
                nearest = visual
            i += 1

        if nearest and min_d < goblin["detection_range"]:
            goblin["target"] = nearest
            goblin["state"] = "attacking"
        else:
            goblin["pos"][0] += random.uniform(-20, 20) * dt
            goblin["pos"][1] += random.uniform(-20, 20) * dt

    def draw(self, surf):
        surf.fill(BG_COLOR)

        view_rect = self.camera.get_view_rect()
        map_part = view_rect.clip(pygame.Rect(0, 0, self.map_width, self.map_height))
        if map_part.width > 0 and map_part.height > 0:
            ms = self.map_surface.subsurface(map_part)
            scaled = pygame.transform.scale(ms, (int(map_part.width * self.camera.zoom),
                                                 int(map_part.height * self.camera.zoom)))
            sx = (view_rect.x - map_part.x) * self.camera.zoom
            sy = (view_rect.y - map_part.y) * self.camera.zoom
            surf.blit(scaled, (sx, sy))

        objs = to_list(self.map_objects)
        n = length(self.map_objects)
        objs_sorted = sorted(objs, key=lambda o: o["pos"][1])
        for obj in objs_sorted:
            r = obj_rect(obj)
            if self.camera.is_visible(r):
                x, y = self.camera.world_to_screen(obj["pos"][0], obj["pos"][1])
                img = obj["image"]
                surf.blit(pygame.transform.scale(
                    img,
                    (int(img.get_width() * self.camera.zoom),
                     int(img.get_height() * self.camera.zoom))
                ), (x, y))

        chars = to_list(self.characters_visual)
        n = length(self.characters_visual)
        i = 0
        while i < n:
            visual = chars[i]
            if not visual["visible"]:
                i += 1
                continue
            p = visual["personaje"]
            frame = visual["frames"][visual.get("frame_index", 0) % len(visual["frames"])]
            x, y = self.camera.world_to_screen(visual["pos"][0], visual["pos"][1])
            sc = pygame.transform.scale(frame,
                                        (int(frame.get_width() * self.camera.zoom),
                                         int(frame.get_height() * self.camera.zoom)))
            surf.blit(sc, (x, y))

            hp = p.salud / 100.0
            bw, bh = 50, 6
            bx, by = x, y - 8
            pygame.draw.rect(surf, (0, 0, 0), pygame.Rect(bx - 1, by - 1, bw + 2, bh + 2))
            pygame.draw.rect(surf, (200, 0, 0), pygame.Rect(bx, by, bw, bh))
            pygame.draw.rect(surf, (0, 200, 0), pygame.Rect(bx, by, bw * hp, bh))
            name_text = self.small_font.render(visual.get('display_name', 'NPC') + " Nv." + str(p.nivel), True, (255, 255, 255))
            surf.blit(name_text, (bx, by - 16))
            i += 1

        gobs = to_list(self.goblins)
        ng = length(self.goblins)
        i = 0
        while i < ng:
            gob = gobs[i]
            if gob["health"] <= 0:
                i += 1
                continue
            x, y = self.camera.world_to_screen(gob["pos"][0], gob["pos"][1])
            frame = gob["frames"][gob.get("frame_index", 0) % len(gob["frames"])]
            sc = pygame.transform.scale(frame,
                                        (int(frame.get_width() * self.camera.zoom),
                                         int(frame.get_height() * self.camera.zoom)))
            surf.blit(sc, (x, y))
            i += 1

        txt = ("📦 " + str(self.inv_mats['madera']) + "🪵 " + str(self.inv_mats['piedra']) + "🪨 | " +
               "🥛 " + str(self.inv_food['leche']) + "  🥚 " + str(self.inv_food['huevos']) + "  🌾 " + str(self.inv_food['trigo']) + " | " +
               "⚔️ " + str(self.goblins_defeated))
        surf.blit(self.small_font.render(txt, True, (200, 200, 200)), (320, 90))

        self.menu3.draw(surf)
        self.terminal.draw(surf)
        self.manager.draw_ui(surf)


def run():
    global current_state, W, H, screen
    current_state = MainMenu()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.VIDEORESIZE:
                W, H = e.w, e.h
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
                if isinstance(current_state, Game):
                    current_state.camera.screen_width = W
                    current_state.camera.screen_height = H
            current_state.handle(e)
        current_state.update(dt)
        current_state.draw(screen)
        if isinstance(current_state, MainMenu) and current_state.next_state is not None:
            current_state = current_state.next_state
        pygame.display.flip()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()