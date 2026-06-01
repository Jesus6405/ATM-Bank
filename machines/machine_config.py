"""
machine_config.py — Configuración de metadatos de las máquinas.

Define nombres descriptivos para estados y símbolos,
y clasifica los símbolos por tipo (red, local, input de usuario).
"""

# =============================================================================
# NOMBRES DESCRIPTIVOS DE ESTADOS
# =============================================================================

NOMBRES_ESTADOS_CAJERO = {
    'q0': 'Cajero en reposo',
    'q1': 'Verificación de estado de tarjeta',
    'q2': 'Esperando ingreso de clave',
    'q3': 'Esperando validación de clave',
    'q4': 'Selección de operación',
    'q5': 'Esperando inserción del monto',
    'q6': 'Comprobación de fondos',
    'q7': 'Esperando inserción de clave nueva',
    'q8': 'Esperando confirmación de clave nueva',
    'q9': 'Tarjeta bloqueada',
    'q10': 'Operación completada',
    'q11': 'Esperando consulta de saldo',
    'q12': 'Comparación de clave',
    'q13': 'Tiempo de espera agotado',
    'q14': 'Esperando confirmación de guardado de clave',
    'q15': 'Error por fondos insuficientes',
    'q16': 'Dispensando dinero',
}

NOMBRES_ESTADOS_BANCO = {
    'p0': 'Esperando conexión',
    'p1': 'Verificando tarjeta',
    'p2': 'Usuario activo',
    'p3': 'Verificando clave',
    'p4': 'Sesión activa',
    'p5': 'Consultando saldo',
    'p6': 'Verificando monto de retiro',
    'p7': 'Guardando nueva clave',
    'p8': 'Operación completada',
    'p9': 'Reversión de cambios',
}

# =============================================================================
# NOMBRES DESCRIPTIVOS DE SÍMBOLOS
# =============================================================================

NOMBRES_SIMBOLOS = {
    # Símbolos del cajero
    'T': 'Inserción de tarjeta',
    'Ch': 'Cuenta habilitada',
    'Cb': 'Cuenta bloqueada',
    'Sco': 'Solicitud de consulta',
    'Sr': 'Solicitud de retiro',
    'Sca': 'Solicitud de cambio de clave',
    'Cl': 'Inserción de la clave',
    'Cok': 'Clave verificada',
    'Cneg': 'Clave incorrecta',
    'N': 'Clave negada 3 veces',
    'Mr': 'Inserción del monto de retiro',
    'Fok': 'Fondos suficientes',
    'Fins': 'Fondos insuficientes',
    'Dr': 'Dinero retirado',
    'Cnu': 'Inserción de clave nueva',
    'Ccnu': 'Confirmación de clave nueva',
    'Cc': 'Claves coinciden',
    'Cnc': 'Claves no coinciden',
    'Cg': 'Clave guardada',
    'S': 'Saldo',
    'E': 'Finalizar / Retirar tarjeta',
    'To': 'Espera agotada',
    'Co': 'Operación cancelada',
    # Símbolos del banco
    'Vt': 'Verificar tarjeta',
    'Ce': 'Conexión establecida',
    'Cr': 'Conexión rechazada',
    'Toc': 'Tiempo de espera del cajero agotado',
    'Rc': 'Revertir cambios',
    'Vcl': 'Verificar clave',
    'Op': 'Operación en proceso',
    'Cn': 'Clave negada',
    'Tif': 'Tres intentos fallidos',
    'Vm': 'Verificar monto',
    'Cs': 'Consultar saldo',
    'Gnu': 'Guardar nueva clave',
    'Mnv': 'Monto inválido',
    'Mv': 'Monto válido',
    'Es': 'Enviar saldo',
    'epsilon': 'Transición automática',
}

# =============================================================================
# CLASIFICACIÓN DE SÍMBOLOS
# =============================================================================

# Símbolos que son mensajes de red (salida de una máquina → entrada de otra)
# Formato: símbolo → máquina destino
SIMBOLOS_RED = {
    # Salidas del cajero → entradas del banco
    'Vt': 'banco',
    'Vcl': 'banco',
    'Vm': 'banco',
    'Cs': 'banco',
    'Gnu': 'banco',
    'Toc': 'banco',
    # Salidas del banco → entradas del cajero
    'Ch': 'cajero',
    'Cb': 'cajero',
    'Cok': 'cajero',
    'Cneg': 'cajero',
    'N': 'cajero',
    'Fok': 'cajero',
    'Fins': 'cajero',
    'S': 'cajero',
    'Cg': 'cajero',
    'E': 'cajero',
}

# Símbolos que representan acciones locales (no se envían a otra máquina)
# Formato: símbolo → descripción de la acción
ACCIONES_LOCALES = {
    'Dr': 'Dispensar billetes al usuario',
}

# Símbolos que son inputs del usuario (introducidos via GUI)
INPUTS_USUARIO = {
    'T': 'Insertar tarjeta',
    'Cl': 'Ingresar clave',
    'Mr': 'Ingresar monto de retiro',
    'Sr': 'Seleccionar retiro',
    'Sca': 'Seleccionar cambio de clave',
    'Sco': 'Seleccionar consulta de saldo',
    'To': 'Timeout (automático)',
    'Co': 'Cancelar operación',
    'Cnu': 'Ingresar nueva clave',
    'Ccnu': 'Confirmar nueva clave',
}

# Símbolos que son decisiones internas del cajero (comparación de claves)
DECISIONES_INTERNAS_CAJERO = {
    'Cc': 'Las claves nuevas coinciden',
    'Cnc': 'Las claves nuevas no coinciden',
}

# Símbolos internos del banco (procesamiento local)
DECISIONES_INTERNAS_BANCO = {
    'Ce': 'Tarjeta verificada correctamente',
    'Cr': 'Tarjeta rechazada',
    'Op': 'Clave verificada correctamente',
    'Cn': 'Clave incorrecta',
    'Tif': 'Tres intentos fallidos detectados',
    'Mv': 'Monto válido verificado',
    'Mnv': 'Monto inválido detectado',
    'Es': 'Saldo consultado',
    'Rc': 'Reversión completada',
    'epsilon': 'Transición automática',
}

# =============================================================================
# COLORES PARA LA VISUALIZACIÓN
# =============================================================================

COLORES_CAJERO = {
    'nodo_normal': '#4A90D9',       # Azul medio
    'nodo_actual': '#2ECC71',       # Verde esmeralda
    'nodo_inicial': '#F39C12',      # Naranja
    'nodo_error': '#E74C3C',        # Rojo
    'arista_normal': '#7F8C8D',     # Gris
    'arista_activa': '#E74C3C',     # Rojo (última transición)
    'texto': '#FFFFFF',             # Blanco
    'fondo': '#1A1A2E',            # Azul oscuro
}

COLORES_BANCO = {
    'nodo_normal': '#8E44AD',       # Púrpura
    'nodo_actual': '#2ECC71',       # Verde esmeralda
    'nodo_inicial': '#F39C12',      # Naranja
    'nodo_error': '#E74C3C',        # Rojo
    'arista_normal': '#7F8C8D',     # Gris
    'arista_activa': '#E67E22',     # Naranja oscuro (última transición)
    'texto': '#FFFFFF',             # Blanco
    'fondo': '#16213E',            # Azul más oscuro
}
