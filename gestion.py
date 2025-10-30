from ListaEnlazada import LinkedList, to_list, find, length, iterate
from deque import Deque


class GestorPoblacion:
    def __init__(self):
        self.enanos_disponibles = Deque()
        self.enanos_ocupados = LinkedList()
        self.enanos_descansando = LinkedList()
        self.visitantes = LinkedList()
        self.enemigos = LinkedList()
        self.todos_enanos = LinkedList()
    
    def agregar_enano(self, enano):
        """Agrega un nuevo enano a la colonia"""
        self.todos_enanos.add(enano)
        if enano.esta_disponible():
            self.enanos_disponibles.push_back(enano)
    
    def obtener_enano_disponible(self):
        """Obtiene el siguiente enano disponible (FIFO)"""
        if not self.enanos_disponibles.empty():
            return self.enanos_disponibles.pop_front()
        return None
    
    def obtener_mejor_enano_para(self, tipo_accion):
        """Busca el mejor enano disponible para una acción específica"""
        if self.enanos_disponibles.empty():
            return None
        
        mejor_enano = None
        mejor_compatibilidad = -1
        temp = []
        
        while not self.enanos_disponibles.empty():
            enano = self.enanos_disponibles.pop_front()
            compatibilidad = enano.calcular_compatibilidad(tipo_accion)
            
            if compatibilidad > mejor_compatibilidad and enano.energia > 20:
                if mejor_enano:
                    temp.append(mejor_enano)
                mejor_enano = enano
                mejor_compatibilidad = compatibilidad
            else:
                temp.append(enano)
        
        for enano in temp:
            self.enanos_disponibles.push_back(enano)
        
        return mejor_enano
    
    def marcar_ocupado(self, enano, accion):
        """Marca un enano como ocupado"""
        enano.asignar_accion(accion)
        self.enanos_ocupados.add(enano)
        
        temp = []
        while not self.enanos_disponibles.empty():
            e = self.enanos_disponibles.pop_front()
            if e != enano:
                temp.append(e)
        
        for e in temp:
            self.enanos_disponibles.push_back(e)
    
    def liberar_enano(self, enano):
        """Libera un enano para que esté disponible nuevamente"""
        resultado = enano.completar_accion()
        self.enanos_ocupados.remove_value(enano)
        
        if enano.energia < 30:
            self.enanos_descansando.add(enano)
        else:
            self.enanos_disponibles.push_back(enano)
        
        return resultado
    
    def actualizar_poblacion(self):
        """Actualiza el estado de todos los enanos"""
        ocupados_temp = to_list(self.enanos_ocupados)
        for enano in ocupados_temp:
            enano.tiempo_ocupado -= 1
            if enano.tiempo_ocupado <= 0:
                self.liberar_enano(enano)
        
        descansando_temp = to_list(self.enanos_descansando)
        for enano in descansando_temp:
            enano.descansar()
            if enano.energia >= 70:
                self.enanos_descansando.remove_value(enano)
                self.enanos_disponibles.push_back(enano)
        
        todos_temp = to_list(self.todos_enanos)
        for enano in todos_temp:
            enano.actualizar_necesidades()
    
    def agregar_visitante(self, personaje):
        """Agrega un visitante (razas aliadas)"""
        self.visitantes.add(personaje)
    
    def agregar_enemigo(self, enemigo):
        """Agrega un enemigo al registro"""
        self.enemigos.add(enemigo)
    
    def remover_enemigo(self, enemigo):
        """Remueve un enemigo derrotado"""
        self.enemigos.remove_value(enemigo)
    
    def obtener_enemigos_activos(self):
        """Obtiene lista de enemigos vivos"""
        enemigos = to_list(self.enemigos)
        return [e for e in enemigos if e.salud > 0]
    
    def obtener_enanos_disponibles(self):
        """Obtiene lista de enanos disponibles sin sacarlos del Deque"""
        temp = []
        disponibles = []
        
        while not self.enanos_disponibles.empty():
            enano = self.enanos_disponibles.pop_front()
            if enano.esta_disponible():
                disponibles.append(enano)
            temp.append(enano)
        
        for enano in temp:
            self.enanos_disponibles.push_back(enano)
        
        return disponibles
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de la población"""
        disponibles_count = 0
        temp = []
        while not self.enanos_disponibles.empty():
            temp.append(self.enanos_disponibles.pop_front())
            disponibles_count += 1
        for e in temp:
            self.enanos_disponibles.push_back(e)
        
        return {
            'total_enanos': length(self.todos_enanos),
            'disponibles': disponibles_count,
            'ocupados': length(self.enanos_ocupados),
            'descansando': length(self.enanos_descansando),
            'visitantes': length(self.visitantes),
            'enemigos': length(self.enemigos),
            'vivos': sum(1 for e in to_list(self.todos_enanos) if e.esta_vivo()),
            'muertos': sum(1 for e in to_list(self.todos_enanos) if not e.esta_vivo())
        }
    
    def mostrar_estado(self):
        """Muestra el estado completo del gestor"""
        stats = self.obtener_estadisticas()
        print("\n" + "="*50)
        print("📊 ESTADO DEL GESTOR DE POBLACIÓN")
        print("="*50)
        print(f"👥 Total enanos: {stats['total_enanos']}")
        print(f"✅ Vivos: {stats['vivos']}")
        print(f"💀 Muertos: {stats['muertos']}")
        print(f"🟢 Disponibles: {stats['disponibles']}")
        print(f"🔵 Ocupados: {stats['ocupados']}")
        print(f"🟡 Descansando: {stats['descansando']}")
        print(f"👋 Visitantes: {stats['visitantes']}")
        print(f"👹 Enemigos: {stats['enemigos']}")
        print("="*50)
    
    def limpiar_muertos(self):
        """Remueve personajes muertos de las listas"""
        todos_temp = to_list(self.todos_enanos)
        muertos_removidos = 0
        
        for enano in todos_temp:
            if not enano.esta_vivo():
                self.enanos_ocupados.remove_value(enano)
                self.enanos_descansando.remove_value(enano)
                muertos_removidos += 1
        
        temp = []
        while not self.enanos_disponibles.empty():
            enano = self.enanos_disponibles.pop_front()
            if enano.esta_vivo():
                temp.append(enano)
        
        for enano in temp:
            self.enanos_disponibles.push_back(enano)
        
        if muertos_removidos > 0:
            print(f"🧹 Limpiados {muertos_removidos} enanos muertos")
