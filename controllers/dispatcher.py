"""
dispatcher.py — Despachador de eventos entre las Máquinas de Mealy.

Coordina la comunicación entre el Cajero y el Banco:
1. Recibe la salida de una máquina.
2. Decide si es un mensaje de red (hacia la otra máquina) o una acción local.
3. Ejecuta la acción correspondiente.
4. Notifica a la GUI de los cambios.
"""

from typing import Optional, Callable
from core.mealy_machine import MaquinaMealy, TransicionInvalida
from controllers.bank_data import DatosBancarios
from machines.machine_config import (
    SIMBOLOS_RED,
    ACCIONES_LOCALES,
    NOMBRES_ESTADOS_CAJERO,
    NOMBRES_ESTADOS_BANCO,
    NOMBRES_SIMBOLOS,
)


class Despachador:
    """
    Despachador central que coordina las dos Máquinas de Mealy
    y gestiona la comunicación entre ellas.
    """

    def __init__(self, cajero: MaquinaMealy, banco: MaquinaMealy,
                 datos_bancarios: DatosBancarios):
        """
        Inicializa el despachador.

        Args:
            cajero: Instancia de la máquina del cajero.
            banco: Instancia de la máquina del banco.
            datos_bancarios: Instancia con los datos bancarios simulados.
        """
        self.cajero = cajero
        self.banco = banco
        self.datos = datos_bancarios

        # Datos temporales de la operación actual
        self._tarjeta_seleccionada: Optional[str] = None
        self._pin_ingresado: Optional[str] = None
        self._monto_ingresado: Optional[float] = None
        self._clave_nueva: Optional[str] = None
        self._confirmacion_clave: Optional[str] = None

        # Callbacks para la GUI
        self._on_log: Optional[Callable] = None
        self._on_estado_cajero: Optional[Callable] = None
        self._on_estado_banco: Optional[Callable] = None
        self._on_accion_local: Optional[Callable] = None
        self._on_transicion_visual: Optional[Callable] = None
        self._on_mensaje_usuario: Optional[Callable] = None

    # =========================================================================
    # REGISTRO DE CALLBACKS
    # =========================================================================

    def registrar_callback_log(self, callback: Callable):
        """Registra callback para agregar entradas al log."""
        self._on_log = callback

    def registrar_callback_estado_cajero(self, callback: Callable):
        """Registra callback para cambios de estado del cajero."""
        self._on_estado_cajero = callback

    def registrar_callback_estado_banco(self, callback: Callable):
        """Registra callback para cambios de estado del banco."""
        self._on_estado_banco = callback

    def registrar_callback_accion_local(self, callback: Callable):
        """Registra callback para acciones locales (dispensar, expulsar, etc.)."""
        self._on_accion_local = callback

    def registrar_callback_transicion_visual(self, callback: Callable):
        """Registra callback para actualizar la visualización de grafos."""
        self._on_transicion_visual = callback

    def registrar_callback_mensaje_usuario(self, callback: Callable):
        """Registra callback para mostrar mensajes al usuario."""
        self._on_mensaje_usuario = callback

    # =========================================================================
    # PROCESAMIENTO DE ENTRADAS DEL USUARIO
    # =========================================================================

    def insertar_tarjeta(self, numero_tarjeta: str):
        """
        Procesa la inserción de una tarjeta por el usuario.

        Args:
            numero_tarjeta: Número de tarjeta seleccionada.
        """
        self._tarjeta_seleccionada = numero_tarjeta
        self._log_info(f"🔲 Usuario inserta tarjeta: {numero_tarjeta}")
        self._procesar_entrada_cajero('T')

    def ingresar_clave(self, pin: str):
        """
        Procesa el ingreso de la clave por el usuario.

        Args:
            pin: PIN ingresado.
        """
        self._pin_ingresado = pin
        self._log_info(f"🔑 Usuario ingresa clave: {'*' * len(pin)}")
        self._procesar_entrada_cajero('Cl')

    def seleccionar_retiro(self):
        """El usuario selecciona la operación de retiro."""
        self._log_info("💰 Usuario selecciona: Retiro")
        self._procesar_entrada_cajero('Sr')

    def seleccionar_consulta_saldo(self):
        """El usuario selecciona consulta de saldo."""
        self._log_info("📊 Usuario selecciona: Consulta de saldo")
        self._procesar_entrada_cajero('Sco')

    def seleccionar_cambio_clave(self):
        """El usuario selecciona cambio de clave."""
        self._log_info("🔐 Usuario selecciona: Cambio de clave")
        self._procesar_entrada_cajero('Sca')

    def ingresar_monto(self, monto: float):
        """
        Procesa el monto de retiro ingresado.

        Args:
            monto: Monto a retirar.
        """
        self._monto_ingresado = monto
        self._log_info(f"💵 Usuario ingresa monto: ${monto:.2f}")
        self._procesar_entrada_cajero('Mr')

    def ingresar_clave_nueva(self, clave: str):
        """
        Procesa la nueva clave ingresada.

        Args:
            clave: Nueva clave.
        """
        self._clave_nueva = clave
        self._log_info(f"🔑 Usuario ingresa nueva clave: {'*' * len(clave)}")
        self._procesar_entrada_cajero('Cnu')

    def confirmar_clave_nueva(self, confirmacion: str):
        """
        Procesa la confirmación de la nueva clave.

        Args:
            confirmacion: Confirmación de la clave.
        """
        self._confirmacion_clave = confirmacion
        self._log_info(f"🔑 Usuario confirma clave: {'*' * len(confirmacion)}")
        self._procesar_entrada_cajero('Ccnu')

    def cancelar_operacion(self):
        """El usuario cancela la operación actual."""
        self._log_info("❌ Usuario cancela la operación")
        self._procesar_entrada_cajero('Co')

    def timeout(self):
        """Se agotó el tiempo de espera."""
        self._log_info("⏰ Tiempo de espera agotado")
        self._procesar_entrada_cajero('To')

    # =========================================================================
    # PROCESAMIENTO INTERNO DE TRANSICIONES
    # =========================================================================

    def _procesar_entrada_cajero(self, simbolo: str):
        """
        Procesa una entrada en la máquina del cajero y despacha la salida.

        Args:
            simbolo: Símbolo de entrada para el cajero.
        """
        try:
            estado_anterior = self.cajero.estado_actual
            nuevo_estado, salida = self.cajero.procesar_entrada(simbolo)

            # Log de la transición
            desc_entrada = NOMBRES_SIMBOLOS.get(simbolo, simbolo)
            desc_salida = NOMBRES_SIMBOLOS.get(salida, salida) if salida else '—'
            desc_estado = NOMBRES_ESTADOS_CAJERO.get(nuevo_estado, nuevo_estado)

            self._log_transicion(
                'CAJERO', estado_anterior, simbolo, desc_entrada,
                salida, desc_salida, nuevo_estado, desc_estado
            )

            # Notificar cambio de estado a la GUI
            if self._on_estado_cajero:
                self._on_estado_cajero(nuevo_estado, desc_estado)
            if self._on_transicion_visual:
                self._on_transicion_visual(
                    'cajero', estado_anterior, nuevo_estado, simbolo, salida
                )

            # Despachar la salida
            if salida:
                self._despachar_salida('cajero', salida)

            # --- TRANSICIONES AUTOMÁTICAS DEL CAJERO ---
            if self.cajero.estado_actual == 'q16':
                # El cajero dispensa dinero y luego avanza a q10 automáticamente con Dr
                self._log_info("💵 Cajero dispensa el dinero al usuario")
                if self._on_accion_local:
                    self._on_accion_local('dispensar_billetes', 'Retire su dinero del dispensador.')
                self._procesar_entrada_cajero('Dr')

        except TransicionInvalida as e:
            self._log_error(str(e))

    def _procesar_entrada_banco(self, simbolo: str):
        """
        Procesa una entrada en la máquina del banco y despacha la salida.

        Args:
            simbolo: Símbolo de entrada para el banco.
        """
        try:
            estado_anterior = self.banco.estado_actual
            nuevo_estado, salida = self.banco.procesar_entrada(simbolo)

            desc_entrada = NOMBRES_SIMBOLOS.get(simbolo, simbolo)
            desc_salida = NOMBRES_SIMBOLOS.get(salida, salida) if salida else '—'
            desc_estado = NOMBRES_ESTADOS_BANCO.get(nuevo_estado, nuevo_estado)

            self._log_transicion(
                'BANCO', estado_anterior, simbolo, desc_entrada,
                salida, desc_salida, nuevo_estado, desc_estado
            )

            if self._on_estado_banco:
                self._on_estado_banco(nuevo_estado, desc_estado)
            if self._on_transicion_visual:
                self._on_transicion_visual(
                    'banco', estado_anterior, nuevo_estado, simbolo, salida
                )

            if salida:
                self._despachar_salida('banco', salida)

            # --- TRANSICIÓN AUTOMÁTICA DEL BANCO ---
            if 'epsilon' in self.banco.obtener_entradas_validas():
                self._procesar_entrada_banco('epsilon')

        except TransicionInvalida as e:
            self._log_error(str(e))

    def _despachar_salida(self, origen: str, simbolo: str):
        """
        Despacha un símbolo de salida: lo envía a la otra máquina
        o ejecuta una acción local.

        Args:
            origen: Máquina que generó la salida ('cajero' o 'banco').
            simbolo: Símbolo de salida a despachar.
        """
        # ¿Es un mensaje de red?
        if simbolo in SIMBOLOS_RED:
            destino = SIMBOLOS_RED[simbolo]
            desc = NOMBRES_SIMBOLOS.get(simbolo, simbolo)
            self._log_info(
                f"📡 Red: {origen.upper()} → {destino.upper()}: "
                f"{simbolo} ({desc})"
            )

            # Antes de enviar, ejecutar lógica de negocio del banco si aplica
            if destino == 'banco':
                self._ejecutar_logica_banco(simbolo)
            elif destino == 'cajero':
                self._ejecutar_logica_cajero_recepcion(simbolo)

        # ¿Es una acción local?
        elif simbolo in ACCIONES_LOCALES:
            desc = ACCIONES_LOCALES[simbolo]
            self._log_info(f"⚙️ Acción local [{origen.upper()}]: {simbolo} ({desc})")
            self._ejecutar_accion_local(origen, simbolo)

        else:
            self._log_info(
                f"⚙️ Símbolo interno [{origen.upper()}]: {simbolo} "
                f"({NOMBRES_SIMBOLOS.get(simbolo, '?')})"
            )

    # =========================================================================
    # LÓGICA DE NEGOCIO DEL BANCO
    # =========================================================================

    def _ejecutar_logica_banco(self, simbolo: str):
        """
        Ejecuta la lógica de negocio del banco y procesa
        la entrada correspondiente en la máquina del banco.

        Args:
            simbolo: Símbolo recibido por el banco.
        """
        if simbolo == 'Vt':
            # Verificar tarjeta
            self._procesar_entrada_banco('Vt')
            if self._tarjeta_seleccionada:
                es_valida, motivo = self.datos.verificar_tarjeta(
                    self._tarjeta_seleccionada
                )
                self._log_info(f"🏦 Banco verifica tarjeta: {motivo}")
                if es_valida:
                    # Ce (conexión establecida) → salida Ch (cuenta habilitada)
                    self._procesar_entrada_banco('Ce')
                else:
                    # Cr (conexión rechazada) → salida Cb (cuenta bloqueada)
                    self._procesar_entrada_banco('Cr')

        elif simbolo == 'Vcl':
            # Verificar clave
            self._procesar_entrada_banco('Vcl')
            if self._pin_ingresado:
                es_correcta, motivo = self.datos.verificar_clave(self._pin_ingresado)
                self._log_info(f"🏦 Banco verifica clave: {motivo}")
                if es_correcta:
                    # Op → salida Cok
                    self._procesar_entrada_banco('Op')
                elif self.datos.intentos_agotados():
                    # Tif → salida N (3 intentos)
                    self._procesar_entrada_banco('Tif')
                else:
                    # Cn → salida Cneg
                    self._procesar_entrada_banco('Cn')
                self._pin_ingresado = None

        elif simbolo == 'Vm':
            # Verificar monto
            self._procesar_entrada_banco('Vm')
            if self._monto_ingresado is not None:
                es_valido, motivo = self.datos.verificar_monto(self._monto_ingresado)
                self._log_info(f"🏦 Banco verifica monto: {motivo}")
                if es_valido:
                    # Mv → salida Fok
                    self._procesar_entrada_banco('Mv')
                else:
                    # Mnv → salida Fins
                    self._procesar_entrada_banco('Mnv')
                self._monto_ingresado = None

        elif simbolo == 'Cs':
            # Consultar saldo
            self._procesar_entrada_banco('Cs')
            saldo, titular = self.datos.consultar_saldo()
            self._log_info(f"🏦 Banco consulta saldo: ${saldo:.2f} ({titular})")
            if self._on_mensaje_usuario:
                self._on_mensaje_usuario(
                    f"Saldo de {titular}: ${saldo:,.2f}"
                )
            # Es → salida S
            self._procesar_entrada_banco('Es')

        elif simbolo == 'Gnu':
            # Guardar nueva clave
            self._procesar_entrada_banco('Gnu')
            if self._clave_nueva:
                exito, motivo = self.datos.guardar_nueva_clave(self._clave_nueva)
                self._log_info(f"🏦 Banco guarda clave: {motivo}")
                # El banco envía Cg (clave guardada) al cajero como confirmación
                self._despachar_salida('banco', 'Cg')
                # Y luego avanza su propio estado internamente
                self._procesar_entrada_banco('Cg')
                self._clave_nueva = None
                self._confirmacion_clave = None

        elif simbolo == 'Toc':
            # Timeout del cajero
            self._procesar_entrada_banco('Toc')
            self._log_info("🏦 Banco recibe timeout del cajero")
            # Rc → revertir cambios
            self._procesar_entrada_banco('Rc')
            self.datos.finalizar_sesion()

    def _ejecutar_logica_cajero_recepcion(self, simbolo: str):
        """
        Procesa un símbolo que el banco envía al cajero.

        Args:
            simbolo: Símbolo recibido por el cajero.
        """
        if simbolo == 'E':
            # El banco envía E al cajero (transición automática epsilon → E)
            self._procesar_entrada_cajero('E')
            self.datos.finalizar_sesion()
            self._limpiar_datos_temporales()
            if self._on_accion_local:
                self._on_accion_local('expulsar_tarjeta',
                                      'Tarjeta expulsada. Gracias por usar nuestro cajero.')
        else:
            # Mensaje normal del banco → entrada al cajero
            self._procesar_entrada_cajero(simbolo)

    # =========================================================================
    # ACCIONES LOCALES
    # =========================================================================

    def _ejecutar_accion_local(self, origen: str, simbolo: str):
        """
        Ejecuta una acción local (no es mensaje de red).

        Args:
            origen: Máquina que generó la salida.
            simbolo: Símbolo de la acción local.
        """
        pass  # Las acciones locales se manejan ahora mediante transiciones automáticas

    # =========================================================================
    # CONTROL DE FLUJO PARA COMPARACIÓN DE CLAVES (cajero local)
    # =========================================================================

    def procesar_comparacion_claves(self):
        """
        Compara la clave nueva con su confirmación.
        Esta es una decisión interna del cajero (no involucra al banco).
        """
        if self._clave_nueva and self._confirmacion_clave:
            if self._clave_nueva == self._confirmacion_clave:
                self._log_info("✅ Las claves coinciden")
                self._procesar_entrada_cajero('Cc')
            else:
                self._log_info("❌ Las claves no coinciden")
                self._procesar_entrada_cajero('Cnc')
                self._clave_nueva = None
                self._confirmacion_clave = None

    def finalizar_operacion(self):
        """
        El usuario finaliza y retira su tarjeta.
        Se usa desde q10 (operación completada), q9, q13, q15.
        """
        self._log_info("🔲 Usuario retira su tarjeta")
        self._procesar_entrada_cajero('E')
        self.datos.finalizar_sesion()
        self._limpiar_datos_temporales()
        if self._on_accion_local:
            self._on_accion_local('expulsar_tarjeta',
                                  'Tarjeta expulsada. Gracias por usar nuestro cajero.')

    # =========================================================================
    # UTILIDADES
    # =========================================================================

    def _limpiar_datos_temporales(self):
        """Limpia todos los datos temporales de la operación."""
        self._tarjeta_seleccionada = None
        self._pin_ingresado = None
        self._monto_ingresado = None
        self._clave_nueva = None
        self._confirmacion_clave = None

    def reiniciar(self):
        """Reinicia completamente el sistema."""
        self.cajero.reiniciar()
        self.banco.reiniciar()
        self.datos.finalizar_sesion()
        self._limpiar_datos_temporales()
        self._log_info("🔄 Sistema reiniciado completamente")
        if self._on_estado_cajero:
            self._on_estado_cajero(
                self.cajero.estado_actual,
                NOMBRES_ESTADOS_CAJERO.get(self.cajero.estado_actual, '')
            )
        if self._on_estado_banco:
            self._on_estado_banco(
                self.banco.estado_actual,
                NOMBRES_ESTADOS_BANCO.get(self.banco.estado_actual, '')
            )

    def obtener_entradas_usuario_validas(self) -> list[str]:
        """
        Retorna las entradas de usuario válidas para el estado actual del cajero.

        Returns:
            Lista de símbolos de entrada que el usuario puede activar.
        """
        return self.cajero.obtener_entradas_validas()

    def _log_transicion(self, maquina: str, estado_origen: str,
                        entrada: str, desc_entrada: str,
                        salida: str | None, desc_salida: str,
                        estado_destino: str, desc_estado: str):
        """Registra una transición en el log."""
        salida_str = salida if salida else '—'
        msg = (
            f"[{maquina}] {estado_origen} --( {entrada}: {desc_entrada} / "
            f"{salida_str}: {desc_salida} )--> {estado_destino}: {desc_estado}"
        )
        if self._on_log:
            self._on_log(maquina, msg)

    def _log_info(self, mensaje: str):
        """Registra un mensaje informativo."""
        if self._on_log:
            self._on_log('INFO', mensaje)

    def _log_error(self, mensaje: str):
        """Registra un mensaje de error."""
        if self._on_log:
            self._on_log('ERROR', f"❗ {mensaje}")
