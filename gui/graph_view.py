"""
graph_view.py — Visualización de grafos de estados con NetworkX + Matplotlib.

Renderiza los diagramas de estados de las Máquinas de Mealy del cajero y banco,
resaltando el estado actual y la última transición en tiempo real.
"""

import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para embeber en Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrowPatch
import customtkinter as ctk
from typing import Optional

from machines.machine_config import (
    NOMBRES_ESTADOS_CAJERO,
    NOMBRES_ESTADOS_BANCO,
    COLORES_CAJERO,
    COLORES_BANCO,
)


class VistaGrafo(ctk.CTkFrame):
    """
    Widget que muestra los grafos de estados de ambas máquinas.

    Utiliza NetworkX para el layout y Matplotlib para el renderizado,
    embebido en un CTkFrame via FigureCanvasTkAgg.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color='#0D1117', corner_radius=12)

        # Crear figura de Matplotlib con dos subplots
        self.fig, (self.ax_cajero, self.ax_banco) = plt.subplots(
            2, 1, figsize=(10, 9),
            facecolor='#0D1117',
            gridspec_kw={'hspace': 0.3}
        )
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)

        # Canvas de Matplotlib embebido en Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)

        # Grafos de NetworkX
        self.grafo_cajero: Optional[nx.DiGraph] = None
        self.grafo_banco: Optional[nx.DiGraph] = None

        # Posiciones de los nodos (calculadas una vez)
        self.pos_cajero: dict = {}
        self.pos_banco: dict = {}

        # Estado actual de cada máquina
        self.estado_actual_cajero: str = 'q0'
        self.estado_actual_banco: str = 'p0'

        # Última transición (para resaltar arista)
        self.ultima_transicion_cajero: Optional[tuple] = None
        self.ultima_transicion_banco: Optional[tuple] = None

    def construir_grafo(self, maquina_id: str, datos_dot: dict):
        """
        Construye el grafo de NetworkX a partir de los datos parseados del DOT.

        Args:
            maquina_id: 'cajero' o 'banco'.
            datos_dot: Diccionario retornado por parsear_dot().
        """
        G = nx.DiGraph()

        # Agregar nodos
        for estado in sorted(datos_dot['estados']):
            G.add_node(estado)

        # Agregar aristas con etiquetas
        for (origen, entrada), (destino, salida) in datos_dot['transiciones'].items():
            etiqueta = f"{entrada}"
            if salida:
                etiqueta += f" / {salida}"
            # Si ya existe una arista, concatenar etiquetas
            if G.has_edge(origen, destino):
                etiqueta_existente = G[origen][destino].get('label', '')
                etiqueta = f"{etiqueta_existente}\n{etiqueta}"
            G.add_edge(origen, destino, label=etiqueta)

        # Calcular layout
        if maquina_id == 'cajero':
            self.grafo_cajero = G
            self.pos_cajero = self._calcular_layout(G, maquina_id)
        else:
            self.grafo_banco = G
            self.pos_banco = self._calcular_layout(G, maquina_id)

    def _calcular_layout(self, G: nx.DiGraph, maquina_id: str) -> dict:
        """
        Calcula las posiciones de los nodos usando un layout optimizado.
        """
        try:
            # Usar Kamada Kawai, que generalmente produce mejores distribuciones
            # para autómatas finitos que spring_layout
            pos = nx.kamada_kawai_layout(G)
        except Exception:
            pos = nx.spring_layout(G, k=3, iterations=150)

        return pos

    def actualizar_estado(self, maquina_id: str, nuevo_estado: str,
                          estado_anterior: Optional[str] = None):
        """
        Actualiza el estado actual de una máquina y re-renderiza.

        Args:
            maquina_id: 'cajero' o 'banco'.
            nuevo_estado: Nombre del nuevo estado.
            estado_anterior: Estado anterior (para resaltar arista).
        """
        if maquina_id == 'cajero':
            self.estado_actual_cajero = nuevo_estado
            if estado_anterior:
                self.ultima_transicion_cajero = (estado_anterior, nuevo_estado)
        else:
            self.estado_actual_banco = nuevo_estado
            if estado_anterior:
                self.ultima_transicion_banco = (estado_anterior, nuevo_estado)

        self._renderizar()

    def _renderizar(self):
        """Re-renderiza ambos grafos."""
        self._renderizar_grafo(
            self.ax_cajero,
            self.grafo_cajero,
            self.pos_cajero,
            'CAJERO — Máquina de Mealy',
            self.estado_actual_cajero,
            self.ultima_transicion_cajero,
            COLORES_CAJERO,
            NOMBRES_ESTADOS_CAJERO,
        )
        self._renderizar_grafo(
            self.ax_banco,
            self.grafo_banco,
            self.pos_banco,
            'BANCO — Máquina de Mealy',
            self.estado_actual_banco,
            self.ultima_transicion_banco,
            COLORES_BANCO,
            NOMBRES_ESTADOS_BANCO,
        )
        self.canvas.draw_idle()

    def _renderizar_grafo(self, ax, grafo: Optional[nx.DiGraph], pos: dict,
                          titulo: str, estado_actual: str,
                          ultima_transicion: Optional[tuple],
                          colores: dict, nombres_estados: dict):
        """
        Renderiza un grafo de estados en un Axes de Matplotlib.
        """
        ax.clear()
        ax.set_facecolor(colores['fondo'])
        ax.set_title(titulo, color='#FFFFFF', fontsize=13,
                     fontweight='bold', pad=10,
                     fontfamily='monospace')

        if grafo is None or len(pos) == 0:
            ax.text(0.5, 0.5, 'Cargando...', ha='center', va='center',
                    color='#FFFFFF', fontsize=14, transform=ax.transAxes)
            return

        nodos = list(grafo.nodes())
        if not nodos:
            return

        # Colores de nodos
        colores_nodos = []
        tamanos_nodos = []
        bordes_nodos = []
        anchos_borde = []

        for nodo in nodos:
            if nodo == estado_actual:
                colores_nodos.append(colores['nodo_actual'])
                tamanos_nodos.append(900)
                bordes_nodos.append('#FFFFFF')
                anchos_borde.append(3.0)
            elif nodo in (grafo.graph.get('estado_inicial', ''),):
                colores_nodos.append(colores['nodo_inicial'])
                tamanos_nodos.append(700)
                bordes_nodos.append(colores['nodo_inicial'])
                anchos_borde.append(2.0)
            else:
                colores_nodos.append(colores['nodo_normal'])
                tamanos_nodos.append(600)
                bordes_nodos.append(colores['nodo_normal'])
                anchos_borde.append(1.5)

        # Dibujar aristas
        aristas = list(grafo.edges())
        colores_aristas = []
        anchos_aristas = []
        estilos_aristas = []
        alphas_aristas = []

        for arista in aristas:
            if ultima_transicion and arista == ultima_transicion:
                colores_aristas.append(colores['arista_activa'])
                anchos_aristas.append(3.0)
                estilos_aristas.append('solid')
                alphas_aristas.append(1.0)
            else:
                colores_aristas.append(colores['arista_normal'])
                anchos_aristas.append(1.0)
                estilos_aristas.append('solid')
                alphas_aristas.append(0.3)  # Reducir opacidad para que no sature la vista

        # Dibujar aristas con flechas
        nx.draw_networkx_edges(
            grafo, pos, ax=ax,
            edgelist=aristas,
            edge_color=colores_aristas,
            width=anchos_aristas,
            arrows=True,
            arrowsize=16,
            arrowstyle='-|>',
            connectionstyle='arc3,rad=0.25', # Curva mayor para evitar superposiciones
            min_source_margin=18,
            min_target_margin=18,
            alpha=alphas_aristas,
        )

        # Dibujar nodos
        nx.draw_networkx_nodes(
            grafo, pos, ax=ax,
            nodelist=nodos,
            node_color=colores_nodos,
            node_size=tamanos_nodos,
            edgecolors=bordes_nodos,
            linewidths=anchos_borde,
            alpha=0.95,
        )

        # Etiquetas de nodos
        etiquetas_nodos = {}
        for nodo in nodos:
            nombre = nombres_estados.get(nodo, nodo)
            if len(nombre) > 18:
                nombre = nombre[:16] + '...'
            etiquetas_nodos[nodo] = f"{nodo}\n{nombre}"

        nx.draw_networkx_labels(
            grafo, pos, ax=ax,
            labels={n: n for n in nodos},
            font_size=9,
            font_color='#FFFFFF',
            font_weight='bold',
            font_family='monospace',
        )

        # Etiquetas de aristas: Mostrar solo para la última transición activa para reducir ruido
        etiquetas_aristas = nx.get_edge_attributes(grafo, 'label')
        etiquetas_activas = {}
        if ultima_transicion and ultima_transicion in etiquetas_aristas:
            etiquetas_activas[ultima_transicion] = etiquetas_aristas[ultima_transicion]

        if etiquetas_activas:
            nx.draw_networkx_edge_labels(
                grafo, pos, ax=ax,
                edge_labels=etiquetas_activas,
                font_size=8,
                font_color='#FFFFFF',
                font_weight='bold',
                font_family='monospace',
                bbox=dict(
                    boxstyle='round,pad=0.3',
                    facecolor=colores['arista_activa'],
                    edgecolor='none',
                    alpha=0.9,
                ),
                rotate=False, # No rotar para mayor legibilidad
            )

        # Leyenda con estado actual
        desc_estado = nombres_estados.get(estado_actual, estado_actual)
        ax.text(
            0.01, 0.02,
            f"Estado actual: {estado_actual} — {desc_estado}",
            transform=ax.transAxes,
            color=colores['nodo_actual'],
            fontsize=9,
            fontweight='bold',
            fontfamily='monospace',
            bbox=dict(
                boxstyle='round,pad=0.4',
                facecolor='#1C1C1C',
                edgecolor=colores['nodo_actual'],
                alpha=0.9,
            ),
        )

        ax.set_xlim(auto=True)
        ax.set_ylim(auto=True)
        ax.margins(0.15)
        ax.axis('off')

    def reiniciar(self):
        """Reinicia la visualización al estado inicial."""
        self.estado_actual_cajero = 'q0'
        self.estado_actual_banco = 'p0'
        self.ultima_transicion_cajero = None
        self.ultima_transicion_banco = None
        self._renderizar()
