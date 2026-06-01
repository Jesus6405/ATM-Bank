"""
app.py — Ventana principal de la aplicación ATM-Bank.

Integra todos los componentes de la GUI:
- Panel de control (izquierda)
- Visualización de grafos (centro)
- Consola de log (derecha)
"""

import os
import customtkinter as ctk
from typing import Optional

from core.mealy_machine import MaquinaMealy
from core.dot_parser import cargar_dot_desde_archivo
from controllers.dispatcher import Despachador
from controllers.bank_data import DatosBancarios
from gui.control_panel import PanelControl
from gui.graph_view import VistaGrafo
from gui.log_view import VistaLog
from machines.machine_config import (
    NOMBRES_ESTADOS_CAJERO,
    NOMBRES_ESTADOS_BANCO,
)


class AplicacionATM(ctk.CTk):
    """
    Ventana principal de la aplicación ATM-Bank.
    """

    def __init__(self, ruta_cajero_dot: str, ruta_banco_dot: str):
        """
        Inicializa la aplicación.

        Args:
            ruta_cajero_dot: Ruta al archivo DOT del cajero.
            ruta_banco_dot: Ruta al archivo DOT del banco.
        """
        super().__init__()

        # Configuración de la ventana
        self.title("🏧 ATM-Bank — Sistema de Máquinas de Mealy")
        self.geometry("1500x900")
        self.minsize(1200, 700)

        # Tema oscuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color='#010409')

        # =====================================================================
        # INICIALIZAR COMPONENTES DEL SISTEMA
        # =====================================================================

        # Cargar las máquinas desde archivos DOT
        datos_cajero = cargar_dot_desde_archivo(ruta_cajero_dot)
        datos_banco = cargar_dot_desde_archivo(ruta_banco_dot)

        self.cajero = MaquinaMealy('cajero', datos_cajero)
        self.banco = MaquinaMealy('banco', datos_banco)

        # Datos bancarios simulados
        self.datos_bancarios = DatosBancarios()

        # Despachador
        self.despachador = Despachador(self.cajero, self.banco, self.datos_bancarios)

        # =====================================================================
        # CONSTRUIR LA INTERFAZ
        # =====================================================================
        self._construir_interfaz(datos_cajero, datos_banco)

        # =====================================================================
        # CONECTAR CALLBACKS
        # =====================================================================
        self._conectar_callbacks()

    def _construir_interfaz(self, datos_cajero: dict, datos_banco: dict):
        """Construye el layout principal de la aplicación."""

        # Barra superior
        self._construir_barra_superior()

        # Container principal con 3 columnas
        self.container = ctk.CTkFrame(self, fg_color='transparent')
        self.container.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        # Configurar grid del container
        self.container.grid_columnconfigure(0, weight=0, minsize=300)  # Panel control
        self.container.grid_columnconfigure(1, weight=1, minsize=500)  # Grafos
        self.container.grid_columnconfigure(2, weight=0, minsize=380)  # Log
        self.container.grid_rowconfigure(0, weight=1)

        # Panel de control (izquierda) — con scroll
        scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            fg_color='#0D1117',
            corner_radius=12,
            width=290,
            scrollbar_button_color='#30363D',
            scrollbar_button_hover_color='#484F58',
        )
        scroll_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 4), pady=0)

        tarjetas = self.datos_bancarios.obtener_tarjetas_disponibles()
        self.panel_control = PanelControl(
            scroll_frame,
            despachador=self.despachador,
            tarjetas=tarjetas,
            fg_color='transparent',
        )
        self.panel_control.pack(fill='both', expand=True)

        # Vista de grafos (centro)
        self.vista_grafos = VistaGrafo(self.container)
        self.vista_grafos.grid(row=0, column=1, sticky='nsew', padx=4, pady=0)

        # Construir grafos
        self.vista_grafos.construir_grafo('cajero', datos_cajero)
        self.vista_grafos.construir_grafo('banco', datos_banco)

        # Log (derecha)
        self.vista_log = VistaLog(self.container, width=370)
        self.vista_log.grid(row=0, column=2, sticky='nsew', padx=(4, 0), pady=0)

        # Renderizado inicial
        self.after(200, self.vista_grafos._renderizar)

    def _construir_barra_superior(self):
        """Construye la barra de título superior."""
        barra = ctk.CTkFrame(self, fg_color='#161B22', height=48, corner_radius=0)
        barra.pack(fill='x', padx=0, pady=(0, 8))
        barra.pack_propagate(False)

        # Título
        ctk.CTkLabel(
            barra,
            text="🏧  ATM-Bank  —  Sistema Distribuido de Máquinas de Mealy",
            font=ctk.CTkFont(family='Consolas', size=15, weight='bold'),
            text_color='#58A6FF',
        ).pack(side='left', padx=20, pady=10)

        # Info
        ctk.CTkLabel(
            barra,
            text="Teoría de la Computación",
            font=ctk.CTkFont(family='Consolas', size=11),
            text_color='#8B949E',
        ).pack(side='right', padx=20, pady=10)

    def _conectar_callbacks(self):
        """Conecta los callbacks del despachador con la GUI."""

        # Log
        self.despachador.registrar_callback_log(
            lambda tipo, msg: self.after(0, self.vista_log.agregar_entrada, tipo, msg)
        )

        # Estado del cajero
        def on_estado_cajero(estado, desc):
            self.after(0, self.panel_control.actualizar_estado_cajero, estado, desc)
            self.after(0, self.vista_grafos.actualizar_estado, 'cajero', estado,
                       self.cajero.historial[-1]['estado_origen']
                       if self.cajero.historial else None)

        self.despachador.registrar_callback_estado_cajero(on_estado_cajero)

        # Estado del banco
        def on_estado_banco(estado, desc):
            self.after(0, self.panel_control.actualizar_estado_banco, estado, desc)
            self.after(0, self.vista_grafos.actualizar_estado, 'banco', estado,
                       self.banco.historial[-1]['estado_origen']
                       if self.banco.historial else None)

        self.despachador.registrar_callback_estado_banco(on_estado_banco)

        # Acciones locales
        def on_accion_local(accion, mensaje):
            self.after(0, self.panel_control.mostrar_mensaje, mensaje)

        self.despachador.registrar_callback_accion_local(on_accion_local)

        # Mensajes al usuario (saldo, etc.)
        def on_mensaje_usuario(mensaje):
            self.after(0, self.panel_control.mostrar_mensaje, mensaje)

        self.despachador.registrar_callback_mensaje_usuario(on_mensaje_usuario)

    def reiniciar(self):
        """Reinicia completamente el sistema."""
        self.despachador.reiniciar()
        self.vista_grafos.reiniciar()
        self.vista_log.limpiar()
