"""
control_panel.py — Panel de control del usuario para el cajero.

Muestra botones y campos de entrada contextuales según el estado actual
de la máquina del cajero. Solo se habilitan las acciones válidas.
"""

import customtkinter as ctk
from typing import Optional, Callable

from machines.machine_config import (
    INPUTS_USUARIO,
    NOMBRES_ESTADOS_CAJERO,
    NOMBRES_ESTADOS_BANCO,
)


class PanelControl(ctk.CTkFrame):
    """
    Panel lateral con botones y campos de entrada para
    interactuar con el cajero.
    """

    def __init__(self, master, despachador, tarjetas: list[dict], **kwargs):
        super().__init__(master, **kwargs)

        self.despachador = despachador
        self.tarjetas = tarjetas

        self.configure(fg_color='#0D1117', corner_radius=12)

        # Referencia a widgets que necesitan actualización
        self._widgets_dinamicos = []

        self._construir_interfaz()

    def _construir_interfaz(self):
        """Construye todos los widgets del panel."""

        # =====================================================================
        # ENCABEZADO
        # =====================================================================
        encabezado = ctk.CTkFrame(self, fg_color='#161B22', corner_radius=10)
        encabezado.pack(fill='x', padx=10, pady=(10, 5))

        ctk.CTkLabel(
            encabezado,
            text="🏧 CAJERO AUTOMÁTICO",
            font=ctk.CTkFont(family='Consolas', size=16, weight='bold'),
            text_color='#58A6FF',
        ).pack(pady=(12, 4))

        ctk.CTkLabel(
            encabezado,
            text="Sistema de Máquinas de Mealy",
            font=ctk.CTkFont(family='Consolas', size=11),
            text_color='#8B949E',
        ).pack(pady=(0, 12))

        # =====================================================================
        # INDICADORES DE ESTADO
        # =====================================================================
        estado_frame = ctk.CTkFrame(self, fg_color='#161B22', corner_radius=10)
        estado_frame.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(
            estado_frame,
            text="Estados Actuales",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            text_color='#C9D1D9',
        ).pack(pady=(10, 5))

        # Estado del cajero
        self.lbl_estado_cajero = ctk.CTkLabel(
            estado_frame,
            text="CAJERO: q0 — Cajero en reposo",
            font=ctk.CTkFont(family='Consolas', size=10),
            text_color='#58A6FF',
            wraplength=250,
        )
        self.lbl_estado_cajero.pack(pady=2, padx=10)

        # Estado del banco
        self.lbl_estado_banco = ctk.CTkLabel(
            estado_frame,
            text="BANCO: p0 — Esperando conexión",
            font=ctk.CTkFont(family='Consolas', size=10),
            text_color='#BC8CFF',
            wraplength=250,
        )
        self.lbl_estado_banco.pack(pady=(2, 10), padx=10)

        # =====================================================================
        # SECCIÓN: TARJETA
        # =====================================================================
        self.frame_tarjeta = ctk.CTkFrame(self, fg_color='#161B22',
                                           corner_radius=10)
        self.frame_tarjeta.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(
            self.frame_tarjeta,
            text="💳 Tarjeta",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            text_color='#C9D1D9',
        ).pack(pady=(10, 5))

        # Selector de tarjeta
        opciones_tarjeta = [
            f"{t['numero']} ({t['titular']}) [{t['estado']}]"
            for t in self.tarjetas
        ]
        self.combo_tarjeta = ctk.CTkComboBox(
            self.frame_tarjeta,
            values=opciones_tarjeta,
            width=260,
            height=32,
            font=ctk.CTkFont(family='Consolas', size=10),
            dropdown_font=ctk.CTkFont(family='Consolas', size=10),
            fg_color='#21262D',
            border_color='#30363D',
            button_color='#30363D',
            button_hover_color='#484F58',
            dropdown_fg_color='#21262D',
            dropdown_hover_color='#30363D',
            text_color='#C9D1D9',
            corner_radius=6,
        )
        self.combo_tarjeta.pack(pady=5, padx=15)
        if opciones_tarjeta:
            self.combo_tarjeta.set(opciones_tarjeta[0])

        self.btn_insertar = ctk.CTkButton(
            self.frame_tarjeta,
            text="📥 Insertar Tarjeta",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            fg_color='#238636',
            hover_color='#2EA043',
            text_color='#FFFFFF',
            height=36,
            width=260,
            corner_radius=8,
            command=self._on_insertar_tarjeta,
        )
        self.btn_insertar.pack(pady=(5, 10), padx=15)

        # =====================================================================
        # SECCIÓN: CLAVE
        # =====================================================================
        self.frame_clave = ctk.CTkFrame(self, fg_color='#161B22',
                                         corner_radius=10)
        self.frame_clave.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(
            self.frame_clave,
            text="🔑 Clave (PIN)",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            text_color='#C9D1D9',
        ).pack(pady=(10, 5))

        self.entry_pin = ctk.CTkEntry(
            self.frame_clave,
            placeholder_text="Ingrese PIN (4 dígitos)",
            show="●",
            width=260,
            height=32,
            font=ctk.CTkFont(family='Consolas', size=12),
            fg_color='#21262D',
            border_color='#30363D',
            text_color='#C9D1D9',
            corner_radius=6,
        )
        self.entry_pin.pack(pady=5, padx=15)

        self.btn_clave = ctk.CTkButton(
            self.frame_clave,
            text="🔓 Verificar Clave",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            fg_color='#1F6FEB',
            hover_color='#388BFD',
            text_color='#FFFFFF',
            height=36,
            width=260,
            corner_radius=8,
            command=self._on_ingresar_clave,
        )
        self.btn_clave.pack(pady=(5, 10), padx=15)

        # =====================================================================
        # SECCIÓN: OPERACIONES
        # =====================================================================
        self.frame_operaciones = ctk.CTkFrame(self, fg_color='#161B22',
                                                corner_radius=10)
        self.frame_operaciones.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(
            self.frame_operaciones,
            text="⚙️ Operaciones",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            text_color='#C9D1D9',
        ).pack(pady=(10, 5))

        botones_frame = ctk.CTkFrame(self.frame_operaciones, fg_color='transparent')
        botones_frame.pack(fill='x', padx=15, pady=5)

        self.btn_retiro = ctk.CTkButton(
            botones_frame,
            text="💰 Retiro",
            font=ctk.CTkFont(family='Consolas', size=11, weight='bold'),
            fg_color='#DA3633',
            hover_color='#F85149',
            text_color='#FFFFFF',
            height=34,
            corner_radius=8,
            command=self._on_retiro,
        )
        self.btn_retiro.pack(fill='x', pady=2)

        self.btn_consulta = ctk.CTkButton(
            botones_frame,
            text="📊 Consulta Saldo",
            font=ctk.CTkFont(family='Consolas', size=11, weight='bold'),
            fg_color='#8957E5',
            hover_color='#A371F7',
            text_color='#FFFFFF',
            height=34,
            corner_radius=8,
            command=self._on_consulta_saldo,
        )
        self.btn_consulta.pack(fill='x', pady=2)

        self.btn_cambio_clave = ctk.CTkButton(
            botones_frame,
            text="🔐 Cambio de Clave",
            font=ctk.CTkFont(family='Consolas', size=11, weight='bold'),
            fg_color='#BF8700',
            hover_color='#D29922',
            text_color='#FFFFFF',
            height=34,
            corner_radius=8,
            command=self._on_cambio_clave,
        )
        self.btn_cambio_clave.pack(fill='x', pady=(2, 10))

        # =====================================================================
        # SECCIÓN: MONTO DE RETIRO
        # =====================================================================
        self.frame_monto = ctk.CTkFrame(self, fg_color='#161B22',
                                         corner_radius=10)
        self.frame_monto.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(
            self.frame_monto,
            text="💵 Monto de Retiro",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            text_color='#C9D1D9',
        ).pack(pady=(10, 5))

        self.entry_monto = ctk.CTkEntry(
            self.frame_monto,
            placeholder_text="Monto (múltiplo de 50)",
            width=260,
            height=32,
            font=ctk.CTkFont(family='Consolas', size=12),
            fg_color='#21262D',
            border_color='#30363D',
            text_color='#C9D1D9',
            corner_radius=6,
        )
        self.entry_monto.pack(pady=5, padx=15)

        self.btn_monto = ctk.CTkButton(
            self.frame_monto,
            text="💸 Confirmar Monto",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            fg_color='#238636',
            hover_color='#2EA043',
            text_color='#FFFFFF',
            height=36,
            width=260,
            corner_radius=8,
            command=self._on_ingresar_monto,
        )
        self.btn_monto.pack(pady=(5, 10), padx=15)

        # =====================================================================
        # SECCIÓN: CAMBIO DE CLAVE
        # =====================================================================
        self.frame_nueva_clave = ctk.CTkFrame(self, fg_color='#161B22',
                                                corner_radius=10)
        self.frame_nueva_clave.pack(fill='x', padx=10, pady=5)

        ctk.CTkLabel(
            self.frame_nueva_clave,
            text="🔑 Nueva Clave",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            text_color='#C9D1D9',
        ).pack(pady=(10, 5))

        self.entry_nueva_clave = ctk.CTkEntry(
            self.frame_nueva_clave,
            placeholder_text="Nueva clave (4 dígitos)",
            show="●",
            width=260,
            height=32,
            font=ctk.CTkFont(family='Consolas', size=12),
            fg_color='#21262D',
            border_color='#30363D',
            text_color='#C9D1D9',
            corner_radius=6,
        )
        self.entry_nueva_clave.pack(pady=5, padx=15)

        self.btn_nueva_clave = ctk.CTkButton(
            self.frame_nueva_clave,
            text="📝 Ingresar Nueva Clave",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            fg_color='#1F6FEB',
            hover_color='#388BFD',
            text_color='#FFFFFF',
            height=36,
            width=260,
            corner_radius=8,
            command=self._on_nueva_clave,
        )
        self.btn_nueva_clave.pack(pady=(5, 5), padx=15)

        self.entry_confirmar_clave = ctk.CTkEntry(
            self.frame_nueva_clave,
            placeholder_text="Confirmar nueva clave",
            show="●",
            width=260,
            height=32,
            font=ctk.CTkFont(family='Consolas', size=12),
            fg_color='#21262D',
            border_color='#30363D',
            text_color='#C9D1D9',
            corner_radius=6,
        )
        self.entry_confirmar_clave.pack(pady=5, padx=15)

        self.btn_confirmar_clave = ctk.CTkButton(
            self.frame_nueva_clave,
            text="✅ Confirmar Clave",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            fg_color='#238636',
            hover_color='#2EA043',
            text_color='#FFFFFF',
            height=36,
            width=260,
            corner_radius=8,
            command=self._on_confirmar_clave,
        )
        self.btn_confirmar_clave.pack(pady=(5, 10), padx=15)

        # =====================================================================
        # SECCIÓN: ACCIONES GENERALES
        # =====================================================================
        self.frame_acciones = ctk.CTkFrame(self, fg_color='#161B22',
                                            corner_radius=10)
        self.frame_acciones.pack(fill='x', padx=10, pady=5)

        acciones_frame = ctk.CTkFrame(self.frame_acciones, fg_color='transparent')
        acciones_frame.pack(fill='x', padx=15, pady=10)

        self.btn_cancelar = ctk.CTkButton(
            acciones_frame,
            text="❌ Cancelar Operación",
            font=ctk.CTkFont(family='Consolas', size=11, weight='bold'),
            fg_color='#6E40C9',
            hover_color='#8957E5',
            text_color='#FFFFFF',
            height=34,
            corner_radius=8,
            command=self._on_cancelar,
        )
        self.btn_cancelar.pack(fill='x', pady=2)

        self.btn_finalizar = ctk.CTkButton(
            acciones_frame,
            text="🔲 Retirar Tarjeta",
            font=ctk.CTkFont(family='Consolas', size=11, weight='bold'),
            fg_color='#DA3633',
            hover_color='#F85149',
            text_color='#FFFFFF',
            height=34,
            corner_radius=8,
            command=self._on_finalizar,
        )
        self.btn_finalizar.pack(fill='x', pady=2)

        self.btn_timeout = ctk.CTkButton(
            acciones_frame,
            text="⏰ Simular Timeout",
            font=ctk.CTkFont(family='Consolas', size=11, weight='bold'),
            fg_color='#484F58',
            hover_color='#6E7681',
            text_color='#C9D1D9',
            height=34,
            corner_radius=8,
            command=self._on_timeout,
        )
        self.btn_timeout.pack(fill='x', pady=2)

        # Separador
        ctk.CTkFrame(self, fg_color='#21262D', height=1).pack(
            fill='x', padx=20, pady=5
        )

        self.btn_reiniciar = ctk.CTkButton(
            self,
            text="🔄 Reiniciar Sistema",
            font=ctk.CTkFont(family='Consolas', size=12, weight='bold'),
            fg_color='#21262D',
            hover_color='#30363D',
            text_color='#F0883E',
            height=36,
            corner_radius=8,
            border_width=1,
            border_color='#F0883E',
            command=self._on_reiniciar,
        )
        self.btn_reiniciar.pack(fill='x', padx=25, pady=(5, 10))

        # =====================================================================
        # MENSAJE AL USUARIO
        # =====================================================================
        self.frame_mensaje = ctk.CTkFrame(self, fg_color='#161B22',
                                           corner_radius=10)
        self.frame_mensaje.pack(fill='x', padx=10, pady=(5, 10))

        self.lbl_mensaje = ctk.CTkLabel(
            self.frame_mensaje,
            text="Bienvenido. Inserte su tarjeta para comenzar.",
            font=ctk.CTkFont(family='Consolas', size=11),
            text_color='#8B949E',
            wraplength=260,
            justify='left',
        )
        self.lbl_mensaje.pack(pady=12, padx=15)

        # Estado inicial de visibilidad
        self._actualizar_visibilidad_secciones()

    # =========================================================================
    # HANDLERS DE EVENTOS
    # =========================================================================

    def _on_insertar_tarjeta(self):
        """Maneja el evento de insertar tarjeta."""
        seleccion = self.combo_tarjeta.get()
        if seleccion:
            # Extraer número de tarjeta del texto del combo
            numero = seleccion.split(' (')[0]
            self.despachador.insertar_tarjeta(numero)
            self._actualizar_visibilidad_secciones()

    def _on_ingresar_clave(self):
        """Maneja el ingreso de la clave."""
        pin = self.entry_pin.get().strip()
        if pin:
            self.entry_pin.delete(0, 'end')
            self.despachador.ingresar_clave(pin)
            self._actualizar_visibilidad_secciones()

    def _on_retiro(self):
        """Maneja la selección de retiro."""
        self.despachador.seleccionar_retiro()
        self._actualizar_visibilidad_secciones()

    def _on_consulta_saldo(self):
        """Maneja la selección de consulta de saldo."""
        self.despachador.seleccionar_consulta_saldo()
        self._actualizar_visibilidad_secciones()

    def _on_cambio_clave(self):
        """Maneja la selección de cambio de clave."""
        self.despachador.seleccionar_cambio_clave()
        self._actualizar_visibilidad_secciones()

    def _on_ingresar_monto(self):
        """Maneja el ingreso del monto de retiro."""
        monto_str = self.entry_monto.get().strip()
        if monto_str:
            try:
                monto = float(monto_str)
                self.entry_monto.delete(0, 'end')
                self.despachador.ingresar_monto(monto)
                self._actualizar_visibilidad_secciones()
            except ValueError:
                self.mostrar_mensaje("⚠️ Ingrese un monto numérico válido.")

    def _on_nueva_clave(self):
        """Maneja el ingreso de la nueva clave."""
        clave = self.entry_nueva_clave.get().strip()
        if clave:
            self.entry_nueva_clave.delete(0, 'end')
            self.despachador.ingresar_clave_nueva(clave)
            self._actualizar_visibilidad_secciones()

    def _on_confirmar_clave(self):
        """Maneja la confirmación de la nueva clave."""
        confirmacion = self.entry_confirmar_clave.get().strip()
        if confirmacion:
            self.entry_confirmar_clave.delete(0, 'end')
            self.despachador.confirmar_clave_nueva(confirmacion)
            # Disparar la comparación de claves (decisión interna del cajero)
            self.after(100, self._procesar_comparacion_claves)

    def _procesar_comparacion_claves(self):
        """Procesa la comparación de claves después de un breve delay."""
        self.despachador.procesar_comparacion_claves()
        self._actualizar_visibilidad_secciones()

    def _on_cancelar(self):
        """Maneja la cancelación de operación."""
        self.despachador.cancelar_operacion()
        self._actualizar_visibilidad_secciones()

    def _on_finalizar(self):
        """Maneja la finalización (retirar tarjeta)."""
        self.despachador.finalizar_operacion()
        self._actualizar_visibilidad_secciones()

    def _on_timeout(self):
        """Simula un timeout."""
        self.despachador.timeout()
        self._actualizar_visibilidad_secciones()

    def _on_reiniciar(self):
        """Reinicia el sistema completo."""
        self.despachador.reiniciar()
        self._actualizar_visibilidad_secciones()
        self.mostrar_mensaje("Sistema reiniciado. Inserte su tarjeta.")

    # =========================================================================
    # ACTUALIZACIÓN DE LA INTERFAZ
    # =========================================================================

    def actualizar_estado_cajero(self, estado: str, descripcion: str):
        """Actualiza el indicador del estado del cajero."""
        self.lbl_estado_cajero.configure(
            text=f"CAJERO: {estado} — {descripcion}"
        )
        self._actualizar_visibilidad_secciones()

    def actualizar_estado_banco(self, estado: str, descripcion: str):
        """Actualiza el indicador del estado del banco."""
        self.lbl_estado_banco.configure(
            text=f"BANCO: {estado} — {descripcion}"
        )

    def mostrar_mensaje(self, mensaje: str):
        """Muestra un mensaje al usuario."""
        self.lbl_mensaje.configure(text=mensaje)

    def _actualizar_visibilidad_secciones(self):
        """
        Actualiza la visibilidad y habilitación de secciones
        según el estado actual del cajero.
        """
        entradas_validas = self.despachador.obtener_entradas_usuario_validas()
        estado = self.despachador.cajero.estado_actual

        # Tarjeta: solo visible en q0
        self._toggle_seccion(self.frame_tarjeta, 'T' in entradas_validas)
        self._toggle_widget(self.btn_insertar, 'T' in entradas_validas)

        # Clave: visible en q2
        self._toggle_seccion(self.frame_clave, 'Cl' in entradas_validas)
        self._toggle_widget(self.btn_clave, 'Cl' in entradas_validas)

        # Operaciones: visible en q4
        self._toggle_seccion(
            self.frame_operaciones,
            any(s in entradas_validas for s in ('Sr', 'Sca', 'Sco'))
        )
        self._toggle_widget(self.btn_retiro, 'Sr' in entradas_validas)
        self._toggle_widget(self.btn_consulta, 'Sco' in entradas_validas)
        self._toggle_widget(self.btn_cambio_clave, 'Sca' in entradas_validas)

        # Monto: visible en q5
        self._toggle_seccion(self.frame_monto, 'Mr' in entradas_validas)
        self._toggle_widget(self.btn_monto, 'Mr' in entradas_validas)

        # Nueva clave: visible en q7, q8
        mostrar_nueva_clave = (
            'Cnu' in entradas_validas or 'Ccnu' in entradas_validas
        )
        self._toggle_seccion(self.frame_nueva_clave, mostrar_nueva_clave)
        self._toggle_widget(self.btn_nueva_clave, 'Cnu' in entradas_validas)
        self._toggle_widget(self.btn_confirmar_clave, 'Ccnu' in entradas_validas)
        self._toggle_widget(self.entry_confirmar_clave, 'Ccnu' in entradas_validas)

        # Cancelar: visible cuando Co es válido
        self._toggle_widget(self.btn_cancelar, 'Co' in entradas_validas)

        # Finalizar (retirar tarjeta): visible cuando E es válido
        self._toggle_widget(self.btn_finalizar, 'E' in entradas_validas)

        # Timeout: visible cuando To es válido
        self._toggle_widget(self.btn_timeout, 'To' in entradas_validas)

        # Actualizar mensaje según estado
        self._actualizar_mensaje_estado(estado)

    def _toggle_seccion(self, frame: ctk.CTkFrame, visible: bool):
        """Muestra u oculta una sección completa."""
        if visible:
            frame.pack(fill='x', padx=10, pady=5)
        else:
            frame.pack_forget()

    def _toggle_widget(self, widget, habilitado: bool):
        """Habilita o deshabilita un widget."""
        if habilitado:
            widget.configure(state='normal')
        else:
            widget.configure(state='disabled')

    def _actualizar_mensaje_estado(self, estado: str):
        """Muestra mensajes contextuales según el estado."""
        mensajes = {
            'q0': 'Bienvenido. Inserte su tarjeta para comenzar.',
            'q1': 'Verificando tarjeta con el banco...',
            'q2': 'Ingrese su clave (PIN) de 4 dígitos.',
            'q3': 'Validando clave con el banco...',
            'q4': 'Seleccione la operación que desea realizar.',
            'q5': 'Ingrese el monto a retirar (múltiplo de 50).',
            'q6': 'Verificando disponibilidad de fondos...',
            'q7': 'Ingrese su nueva clave de 4 dígitos.',
            'q8': 'Confirme su nueva clave.',
            'q9': '⚠️ Su tarjeta ha sido bloqueada. Retire su tarjeta.',
            'q10': '✅ Operación completada. Retire su tarjeta.',
            'q11': 'Consultando saldo con el banco...',
            'q12': 'Comparando claves...',
            'q13': '⏰ Tiempo de espera agotado. Retire su tarjeta.',
            'q14': 'Guardando nueva clave en el banco...',
            'q15': '❌ Fondos insuficientes. Retire su tarjeta.',
            'q16': '💵 Dispensando dinero. Por favor espere...',
        }
        msg = mensajes.get(estado, '')
        if msg:
            self.mostrar_mensaje(msg)
