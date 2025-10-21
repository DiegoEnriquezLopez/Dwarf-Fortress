


from proyecto.lista_enlazada import ListaEnlazada
from proyecto.deque import Deque

class GestorPoblacion:
    """Gestiona la población de enanos y personajes usando estructuras propias"""
    def __init__(self):
        self.enanos_disponibles = Deque()  # Enanos listos para trabajar
        self.enanos_ocupados = ListaEnlazada()  # Enanos trabajando
        self.enanos_descansando = ListaEnlazada()  # Enanos recuperándose
        self.visitantes = ListaEnlazada()  # Razas aliadas visitantes
        self.enemigos = ListaEnlazada()  # Enemigos en el mapa
        self.todos_enanos = ListaEnlazada()  # Registro completo
    
    def agregar_enano(self, enano):
        """Agrega un nuevo enano a la colonia"""
        self.todos_enanos.agregar_al_final(enano)
        if enano.esta_disponible():
            self.enanos_disponibles.agregar_atras(enano)
    
    def obtener_enano_disponible(self):
        """Obtiene el siguiente enano disponible (FIFO)"""
        if not self.enanos_disponibles.esta_vacia():
            return self.enanos_disponibles.quitar_frente()
        return None
    
    def obtener_mejor_enano_para(self, tipo_accion):
        """Busca el mejor enano disponible para una acción específica"""
        mejor_enano = None
        mejor_compatibilidad = -1
        
        for enano in self.enanos_disponibles:
            compatibilidad = enano.calcular_compatibilidad(tipo_accion)
            if compatibilidad > mejor_compatibilidad and enano.energia > 20:
                mejor_compatibilidad = compatibilidad
                mejor_enano = enano
        
        if mejor_enano:
            # Remover del deque
            temp_lista = []
            while not self.enanos_disponibles.esta_vacia():
                enano = self.enanos_disponibles.quitar_frente()
                if enano != mejor_enano:
                    temp_lista.append(enano)
            
            for enano in temp_lista:
                self.enanos_disponibles.agregar_atras(enano)
        
        return mejor_enano
    
    def marcar_ocupado(self, enano, accion):
        """Marca un enano como ocupado"""
        enano.asignar_accion(accion)
        self.enanos_ocupados.agregar_al_final(enano)
    
    def liberar_enano(self, enano):
        """Libera un enano para que esté disponible nuevamente"""
        resultado = enano.completar_accion()
        self.enanos_ocupados.eliminar(enano)
        
        if enano.energia < 30:
            self.enanos_descansando.agregar_al_final(enano)
        else:
            self.enanos_disponibles.agregar_atras(enano)
        
        return resultado
    
    def actualizar_poblacion(self):
        """Actualiza el estado de todos los enanos"""
        # Actualizar enanos ocupados
        for enano in list(self.enanos_ocupados):
            enano.tiempo_ocupado -= 1
            if enano.tiempo_ocupado <= 0:
                self.liberar_enano(enano)
        
        # Actualizar enanos descansando
        for enano in list(self.enanos_descansando):
            enano.descansar()
            if enano.energia >= 70:
                self.enanos_descansando.eliminar(enano)
                self.enanos_disponibles.agregar_atras(enano)
        
        # Actualizar necesidades
        for enano in self.todos_enanos:
            enano.actualizar_necesidades()
    
    def agregar_visitante(self, personaje):
        """Agrega un visitante (razas aliadas)"""
        self.visitantes.agregar_al_final(personaje)
    
    def agregar_enemigo(self, enemigo):
        """Agrega un enemigo al registro"""
        self.enemigos.agregar_al_final(enemigo)
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de la población"""
        return {
            'total_enanos': len(self.todos_enanos),
            'disponibles': self.enanos_disponibles.tamanio(),
            'ocupados': len(self.enanos_ocupados),
            'descansando': len(self.enanos_descansando),
            'visitantes': len(self.visitantes),
            'enemigos': len(self.enemigos)
        }
