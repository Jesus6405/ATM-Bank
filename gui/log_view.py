"""
log_view.py — Consola de log de transiciones.

Muestra el historial de transiciones y eventos del sistema,
con colores diferenciados por tipo de máquina.
"""

import customtkinter as ctk
from datetime import datetime


class VistaLog(ctk.CTkFrame):
    """
    Widget que muestra el log de transiciones y eventos del sistema.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color='#0D1117', corner_radius=12)

        # Título
        titulo_frame = ctk.CTkFrame(self, fg_color='transparent')
        titulo_frame.pack(fill='x', padx=10, pady=(10, 5))

        ctk.CTkLabel(
            titulo_frame,
            text="📋 Consola de Transiciones",
            font=ctk.CTkFont(family='Consolas', size=14, weight='bold'),
            text_color='#E0E0E0',
        ).pack(side='left')

        # Botón limpiar
        btn_limpiar = ctk.CTkButton(
            titulo_frame,
            text="🗑️ Limpiar",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color='#2D2D2D',
            hover_color='#3D3D3D',
            text_color='#AAAAAA',
            corner_radius=6,
            command=self.limpiar,
        )
        btn_limpiar.pack(side='right')

        # Área de texto con scroll
        self.texto = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family='Consolas', size=11),
            fg_color='#161B22',
            text_color='#C9D1D9',
            corner_radius=8,
            border_width=1,
            border_color='#30363D',
            wrap='word',
            state='disabled',
        )
        self.texto.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Configurar tags de colores
        self.texto.configure(state='normal')
        self.texto._textbox.tag_configure('cajero', foreground='#58A6FF')
        self.texto._textbox.tag_configure('banco', foreground='#BC8CFF')
        self.texto._textbox.tag_configure('info', foreground='#8B949E')
        self.texto._textbox.tag_configure('error', foreground='#F85149')
        self.texto._textbox.tag_configure('timestamp', foreground='#484F58')
        self.texto._textbox.tag_configure('separador', foreground='#21262D')
        self.texto.configure(state='disabled')

        # Mensaje inicial
        self.agregar_entrada(
            'INFO',
            '🚀 Sistema ATM-Bank iniciado. Esperando operaciones...'
        )
        self.agregar_entrada(
            'INFO',
            '━' * 55
        )

    def agregar_entrada(self, tipo: str, mensaje: str):
        """
        Agrega una entrada al log.

        Args:
            tipo: Tipo de entrada ('CAJERO', 'BANCO', 'INFO', 'ERROR').
            mensaje: Texto del mensaje.
        """
        self.texto.configure(state='normal')

        # Timestamp
        ahora = datetime.now().strftime('%H:%M:%S')
        tag = tipo.lower() if tipo.lower() in ('cajero', 'banco', 'info', 'error') else 'info'

        # Insertar timestamp
        self.texto._textbox.insert('end', f"[{ahora}] ", 'timestamp')

        # Insertar mensaje con color
        self.texto._textbox.insert('end', f"{mensaje}\n", tag)

        # Auto-scroll al final
        self.texto._textbox.see('end')
        self.texto.configure(state='disabled')

    def limpiar(self):
        """Limpia todo el contenido del log."""
        self.texto.configure(state='normal')
        self.texto._textbox.delete('1.0', 'end')
        self.texto.configure(state='disabled')
        self.agregar_entrada(
            'INFO',
            '🗑️ Log limpiado. Esperando operaciones...'
        )
        self.agregar_entrada(
            'INFO',
            '━' * 55
        )
