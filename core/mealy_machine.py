"""
mealy_machine.py — Clase base genérica para Máquinas de Mealy.

Una Máquina de Mealy es un autómata finito donde las salidas dependen
tanto del estado actual como del símbolo de entrada.

Definición formal: M = (Q, Σ, Ω, δ, λ, q₀)
    - Q: Conjunto finito de estados
    - Σ: Alfabeto de entrada
    - Ω: Alfabeto de salida
    - δ: Función de transición Q × Σ → Q
    - λ: Función de salida Q × Σ → Ω
    - q₀: Estado inicial
"""

from typing import Optional, Callable
from core.dot_parser import parsear_dot, cargar_dot_desde_archivo


class MaquinaMealy:
    """
    Implementación genérica de una Máquina de Mealy.

    Construida a partir de datos parseados de formato DOT o configuración manual.
    """

    def __init__(self, nombre: str, datos_dot: dict):
        """
        Inicializa la Máquina de Mealy.

        Args:
            nombre: Nombre identificador de la máquina (ej. "cajero", "banco").
            datos_dot: Diccionario retornado por parsear_dot() con:
                - estados, estado_inicial, transiciones,
                  alfabeto_entrada, alfabeto_salida
        """
        self.nombre = nombre
        self.estados: set[str] = datos_dot['estados']
        self.estado_inicial: str = datos_dot['estado_inicial']
        self.estado_actual: str = self.estado_inicial
        self.transiciones: dict[tuple[str, str], tuple[str, Optional[str]]] = (
            datos_dot['transiciones']
        )
        self.alfabeto_entrada: set[str] = datos_dot['alfabeto_entrada']
        self.alfabeto_salida: set[str] = datos_dot['alfabeto_salida']
        self.historial: list[dict] = []

        # Callbacks para notificar cambios
        self._on_transicion: Optional[Callable] = None
        self._on_cambio_estado: Optional[Callable] = None

    def registrar_callback_transicion(self, callback: Callable):
        """Registra un callback que se invoca en cada transición."""
        self._on_transicion = callback

    def registrar_callback_cambio_estado(self, callback: Callable):
        """Registra un callback que se invoca en cada cambio de estado."""
        self._on_cambio_estado = callback

    def procesar_entrada(self, simbolo: str) -> tuple[str, Optional[str]]:
        """
        Procesa un símbolo de entrada y ejecuta la transición correspondiente.

        Args:
            simbolo: Símbolo de entrada a procesar.

        Returns:
            Tupla (nuevo_estado, simbolo_salida).
            simbolo_salida puede ser None si la transición no produce salida.

        Raises:
            TransicionInvalida: Si no existe transición para el par
                                (estado_actual, simbolo).
        """
        clave = (self.estado_actual, simbolo)

        if clave not in self.transiciones:
            raise TransicionInvalida(
                f"[{self.nombre}] No existe transición desde '{self.estado_actual}' "
                f"con entrada '{simbolo}'. "
                f"Entradas válidas: {self.obtener_entradas_validas()}"
            )

        estado_anterior = self.estado_actual
        nuevo_estado, salida = self.transiciones[clave]
        self.estado_actual = nuevo_estado

        # Registrar en historial
        registro = {
            'maquina': self.nombre,
            'estado_origen': estado_anterior,
            'entrada': simbolo,
            'salida': salida,
            'estado_destino': nuevo_estado,
        }
        self.historial.append(registro)

        # Notificar callbacks
        if self._on_transicion:
            self._on_transicion(registro)
        if self._on_cambio_estado:
            self._on_cambio_estado(self.nombre, nuevo_estado)

        return nuevo_estado, salida

    def obtener_entradas_validas(self) -> list[str]:
        """
        Retorna la lista de símbolos de entrada válidos para el estado actual.

        Returns:
            Lista de símbolos de entrada que producen transiciones válidas.
        """
        entradas = []
        for (estado, entrada) in self.transiciones:
            if estado == self.estado_actual:
                entradas.append(entrada)
        return sorted(entradas)

    def obtener_transiciones_desde(self, estado: str) -> list[dict]:
        """
        Retorna las transiciones que salen de un estado dado.

        Args:
            estado: Nombre del estado.

        Returns:
            Lista de diccionarios con info de cada transición.
        """
        resultado = []
        for (est, entrada), (destino, salida) in self.transiciones.items():
            if est == estado:
                resultado.append({
                    'estado_origen': est,
                    'entrada': entrada,
                    'salida': salida,
                    'estado_destino': destino,
                })
        return resultado

    def reiniciar(self):
        """Reinicia la máquina al estado inicial."""
        self.estado_actual = self.estado_inicial
        self.historial.clear()
        if self._on_cambio_estado:
            self._on_cambio_estado(self.nombre, self.estado_actual)

    def obtener_info_estado(self) -> dict:
        """
        Retorna información del estado actual para la GUI.

        Returns:
            Diccionario con nombre, estado actual, entradas válidas.
        """
        return {
            'maquina': self.nombre,
            'estado_actual': self.estado_actual,
            'entradas_validas': self.obtener_entradas_validas(),
            'es_estado_inicial': self.estado_actual == self.estado_inicial,
        }

    def __repr__(self) -> str:
        return (
            f"MaquinaMealy(nombre='{self.nombre}', "
            f"estado_actual='{self.estado_actual}', "
            f"estados={len(self.estados)}, "
            f"transiciones={len(self.transiciones)})"
        )

    @classmethod
    def desde_archivo_dot(cls, nombre: str, ruta: str) -> 'MaquinaMealy':
        """
        Crea una MaquinaMealy a partir de un archivo DOT.

        Args:
            nombre: Nombre de la máquina.
            ruta: Ruta al archivo .dot

        Returns:
            Instancia de MaquinaMealy configurada.
        """
        datos = cargar_dot_desde_archivo(ruta)
        return cls(nombre, datos)

    @classmethod
    def desde_cadena_dot(cls, nombre: str, cadena: str) -> 'MaquinaMealy':
        """
        Crea una MaquinaMealy a partir de una cadena DOT.

        Args:
            nombre: Nombre de la máquina.
            cadena: String con contenido DOT.

        Returns:
            Instancia de MaquinaMealy configurada.
        """
        datos = parsear_dot(cadena)
        return cls(nombre, datos)


class TransicionInvalida(Exception):
    """Excepción lanzada cuando se intenta una transición no válida."""
    pass
