# Máquinas de Mealy

El funcionamiento del sistema ATM-Bank está estrictamente modelado mediante dos **Máquinas de Mealy** que interactúan entre sí.

Una Máquina de Mealy es un autómata finito en el cual las salidas están determinadas tanto por el *estado actual* como por el *símbolo de entrada* actual. En este sistema, las salidas de una máquina actúan a menudo como entradas de la otra, estableciendo un protocolo de comunicación.

La definición formal de cada máquina es una 6-tupla: $M = (Q, \Sigma, \Omega, \delta, \lambda, q_0)$.

---

## 1. Máquina del Cajero Automático (ATM)

### Estados ($Q_{Cajero}$)
Los estados del cajero ($q_0$ a $q_{16}$) modelan la interfaz directa con el usuario:
- **$q_0$**: Cajero en reposo.
- **$q_1$**: Verificación de estado de tarjeta.
- **$q_2$**: Esperando ingreso de clave.
- **$q_3$**: Esperando validación de clave.
- **$q_4$**: Selección de operación (menú principal).
- **$q_5$**: Esperando inserción del monto.
- **$q_6$**: Comprobación de fondos.
- **$q_7$**: Esperando inserción de clave nueva.
- **$q_8$**: Esperando confirmación de clave nueva.
- **$q_9$**: Tarjeta bloqueada.
- **$q_{10}$**: Operación completada.
- **$q_{11}$**: Esperando consulta de saldo.
- **$q_{12}$**: Comparación de clave.
- **$q_{13}$**: Tiempo de espera agotado.
- **$q_{14}$**: Esperando confirmación de guardado de clave.
- **$q_{15}$**: Error por fondos insuficientes.
- **$q_{16}$**: Dispensando dinero.

### Estado Inicial ($q_0$)
El estado de partida es $q_0$.

### Alfabeto de Entrada ($\Sigma_{Cajero}$)
Conjunto de símbolos que el Cajero puede recibir (ya sea acciones del usuario o respuestas del Banco):
*De Usuario:* `T` (Insertar Tarjeta), `Cl` (Ingresar Clave), `Sr` (Seleccionar Retiro), `Sco` (Consulta Saldo), `Sca` (Cambio Clave), `Mr` (Ingresar Monto), `Cnu` (Clave nueva), `Ccnu` (Confirmar clave nueva), `Co` (Cancelar).
*Internos/Decisiones:* `Cc` (Claves coinciden), `Cnc` (No coinciden), `To` (Timeout).
*Desde el Banco:* `Ch` (Cuenta Habilitada), `Cb` (Cuenta bloqueada), `Cok` (Clave correcta), `Cneg` (Clave incorrecta), `N` (Bloqueo por intentos), `Fok` (Fondos OK), `Fins` (Fondos insuficientes), `S` (Saldo recibido), `Cg` (Clave guardada), `E` (Expulsar).

### Alfabeto de Salida ($\Omega_{Cajero}$)
Acciones generadas por las transiciones del Cajero:
*Hacia el Banco:* `Vt` (Verificar Tarjeta), `Vcl` (Verificar Clave), `Vm` (Verificar Monto), `Cs` (Consultar Saldo), `Gnu` (Guardar Nueva Clave), `Toc` (Notificar Timeout).
*Locales:* `Dr` (Dispensar billetes).

---

## 2. Máquina del Banco (Servidor)

### Estados ($Q_{Banco}$)
Los estados del banco ($p_0$ a $p_9$) modelan la lógica de negocio y las verificaciones contra la base de datos:
- **$p_0$**: Esperando conexión.
- **$p_1$**: Verificando tarjeta.
- **$p_2$**: Usuario activo (esperando credenciales).
- **$p_3$**: Verificando clave.
- **$p_4$**: Sesión activa (listo para procesar operaciones).
- **$p_5$**: Consultando saldo.
- **$p_6$**: Verificando monto de retiro.
- **$p_7$**: Guardando nueva clave.
- **$p_8$**: Operación completada.
- **$p_9$**: Reversión de cambios (rollback ante fallos/timeout).

### Estado Inicial ($q_0$)
El estado de partida es $p_0$.

### Alfabeto de Entrada ($\Sigma_{Banco}$)
Símbolos enviados por el Cajero hacia el Banco, y decisiones internas del propio Banco tras validar la información en su base de datos.
*Desde el Cajero:* `Vt`, `Vcl`, `Vm`, `Cs`, `Gnu`, `Toc`.
*Decisiones Internas de la Base de Datos:* `Ce` (Conexión Establecida/Tarjeta OK), `Cr` (Tarjeta Rechazada), `Op` (Clave OK), `Cn` (Clave errónea), `Tif` (Tres intentos fallidos), `Mv` (Monto válido), `Mnv` (Monto inválido), `Es` (Enviar Saldo), `Rc` (Revertir cambios), `epsilon` (Transición automática).

### Alfabeto de Salida ($\Omega_{Banco}$)
Mensajes que el Banco envía de vuelta al Cajero tras procesar las entradas:
*Hacia el Cajero:* `Ch` (Cuenta Habilitada), `Cb` (Cuenta bloqueada), `Cok` (Clave verificada), `Cneg` (Clave incorrecta), `N` (Clave negada 3 veces), `Fok` (Fondos suficientes), `Fins` (Fondos insuficientes), `S` (Saldo), `Cg` (Clave guardada), `E` (Expulsar / Finalizar sesión).

---

## 3. Dinámica de Transiciones e Intercambio de Mensajes

La función de transición ($\delta$) y la función de salida ($\lambda$) están definidas implícitamente en los archivos Graphviz `.dot` (`cajero.dot` y `banco.dot`), donde los nodos son los estados y los arcos tienen el formato `Entrada / Salida`.

**Ejemplo de Transición - Inicio de Sesión:**
1. Cajero en $q_0$. Recibe `T`. Transición: $q_0 \xrightarrow{T / Vt} q_1$. El cajero envía `Vt`.
2. Banco en $p_0$. Recibe `Vt`. Transición: $p_0 \xrightarrow{Vt / -} p_1$.
3. El Banco verifica la tarjeta. Si es válida, internamente genera `Ce`.
4. Banco en $p_1$. Recibe `Ce`. Transición: $p_1 \xrightarrow{Ce / Ch} p_2$. El Banco envía `Ch`.
5. Cajero en $q_1$. Recibe `Ch`. Transición: $q_1 \xrightarrow{Ch / -} q_2$. El cajero ahora espera el PIN.
