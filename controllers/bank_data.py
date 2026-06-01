"""
bank_data.py — Datos bancarios simulados (hardcodeados en memoria).

Provee funciones para simular operaciones bancarias:
verificación de tarjeta, validación de clave, consulta de saldo,
verificación de monto, cambio de clave y bloqueo de cuenta.
"""


class DatosBancarios:
    """
    Simula la base de datos del banco con cuentas de prueba.
    """

    def __init__(self):
        """Inicializa las cuentas de prueba."""
        self.cuentas = {
            '4000-0000-0001': {
                'titular': 'Juan Pérez',
                'pin': '1234',
                'saldo': 15000.00,
                'estado': 'activa',
                'intentos_fallidos': 0,
            },
            '4000-0000-0002': {
                'titular': 'María García',
                'pin': '5678',
                'saldo': 3500.50,
                'estado': 'activa',
                'intentos_fallidos': 0,
            },
            '4000-0000-0003': {
                'titular': 'Carlos López',
                'pin': '0000',
                'saldo': 250.00,
                'estado': 'activa',
                'intentos_fallidos': 0,
            },
            '4000-0000-0004': {
                'titular': 'Ana Martínez',
                'pin': '9999',
                'saldo': 50000.00,
                'estado': 'bloqueada',
                'intentos_fallidos': 3,
            },
        }
        # Tarjeta actualmente en uso
        self.tarjeta_actual = None
        # Clave nueva temporal (para cambio de clave)
        self._clave_nueva_temporal = None

    def verificar_tarjeta(self, numero_tarjeta: str) -> tuple[bool, str]:
        """
        Verifica si una tarjeta existe y está habilitada.

        Args:
            numero_tarjeta: Número de la tarjeta.

        Returns:
            Tupla (es_valida, motivo).
        """
        if numero_tarjeta not in self.cuentas:
            return False, 'Tarjeta no encontrada'

        cuenta = self.cuentas[numero_tarjeta]
        if cuenta['estado'] == 'bloqueada':
            return False, 'Cuenta bloqueada'

        self.tarjeta_actual = numero_tarjeta
        return True, 'Tarjeta verificada correctamente'

    def verificar_clave(self, pin: str) -> tuple[bool, str]:
        """
        Verifica la clave (PIN) de la tarjeta actual.

        Args:
            pin: PIN ingresado por el usuario.

        Returns:
            Tupla (es_correcta, motivo).
            Si se alcanzan 3 intentos fallidos, bloquea la cuenta.
        """
        if self.tarjeta_actual is None:
            return False, 'No hay tarjeta insertada'

        cuenta = self.cuentas[self.tarjeta_actual]

        if cuenta['pin'] == pin:
            cuenta['intentos_fallidos'] = 0
            return True, 'Clave correcta'
        else:
            cuenta['intentos_fallidos'] += 1
            intentos = cuenta['intentos_fallidos']

            if intentos >= 3:
                cuenta['estado'] = 'bloqueada'
                return False, f'Clave incorrecta. Cuenta bloqueada ({intentos}/3 intentos)'
            else:
                return False, f'Clave incorrecta ({intentos}/3 intentos)'

    def intentos_agotados(self) -> bool:
        """Verifica si se agotaron los 3 intentos de clave."""
        if self.tarjeta_actual is None:
            return False
        cuenta = self.cuentas[self.tarjeta_actual]
        return cuenta['intentos_fallidos'] >= 3

    def consultar_saldo(self) -> tuple[float, str]:
        """
        Consulta el saldo de la tarjeta actual.

        Returns:
            Tupla (saldo, titular).
        """
        if self.tarjeta_actual is None:
            return 0.0, 'No hay tarjeta insertada'

        cuenta = self.cuentas[self.tarjeta_actual]
        return cuenta['saldo'], cuenta['titular']

    def verificar_monto(self, monto: float) -> tuple[bool, str]:
        """
        Verifica si el monto de retiro es válido.

        Args:
            monto: Monto solicitado para retiro.

        Returns:
            Tupla (es_valido, motivo).
        """
        if self.tarjeta_actual is None:
            return False, 'No hay tarjeta insertada'

        if monto <= 0:
            return False, 'El monto debe ser mayor a 0'

        if monto % 50 != 0:
            return False, 'El monto debe ser múltiplo de 50'

        cuenta = self.cuentas[self.tarjeta_actual]
        if monto > cuenta['saldo']:
            return False, f'Fondos insuficientes. Saldo: ${cuenta["saldo"]:.2f}'

        # Realizar el retiro
        cuenta['saldo'] -= monto
        return True, f'Retiro de ${monto:.2f} aprobado. Nuevo saldo: ${cuenta["saldo"]:.2f}'

    def guardar_nueva_clave(self, nueva_clave: str) -> tuple[bool, str]:
        """
        Guarda una nueva clave para la tarjeta actual.

        Args:
            nueva_clave: Nueva clave (PIN) a guardar.

        Returns:
            Tupla (exito, motivo).
        """
        if self.tarjeta_actual is None:
            return False, 'No hay tarjeta insertada'

        if len(nueva_clave) != 4 or not nueva_clave.isdigit():
            return False, 'La clave debe ser de 4 dígitos numéricos'

        cuenta = self.cuentas[self.tarjeta_actual]
        cuenta['pin'] = nueva_clave
        return True, 'Clave actualizada correctamente'

    def bloquear_cuenta(self) -> tuple[bool, str]:
        """
        Bloquea la cuenta de la tarjeta actual.

        Returns:
            Tupla (exito, motivo).
        """
        if self.tarjeta_actual is None:
            return False, 'No hay tarjeta insertada'

        cuenta = self.cuentas[self.tarjeta_actual]
        cuenta['estado'] = 'bloqueada'
        return True, f'Cuenta de {cuenta["titular"]} bloqueada'

    def finalizar_sesion(self):
        """Finaliza la sesión actual y libera la tarjeta."""
        self.tarjeta_actual = None
        self._clave_nueva_temporal = None

    def obtener_tarjetas_disponibles(self) -> list[dict]:
        """
        Retorna la lista de tarjetas disponibles para la GUI.

        Returns:
            Lista de diccionarios con número y titular.
        """
        tarjetas = []
        for numero, cuenta in self.cuentas.items():
            tarjetas.append({
                'numero': numero,
                'titular': cuenta['titular'],
                'estado': cuenta['estado'],
            })
        return tarjetas

    def obtener_info_cuenta_actual(self) -> dict | None:
        """Retorna info de la cuenta asociada a la tarjeta actual."""
        if self.tarjeta_actual is None:
            return None
        cuenta = self.cuentas[self.tarjeta_actual]
        return {
            'numero': self.tarjeta_actual,
            'titular': cuenta['titular'],
            'saldo': cuenta['saldo'],
            'estado': cuenta['estado'],
            'intentos_fallidos': cuenta['intentos_fallidos'],
        }
