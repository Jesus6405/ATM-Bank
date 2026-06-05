# Manual de Usuario del ATM-Bank

Bienvenido al simulador de Cajero Automático (ATM-Bank). Esta guía te ayudará a entender cómo interactuar con la aplicación y visualizar en tiempo real el comportamiento de los autómatas subyacentes.

---

## 1. Inicio Rápido

Para iniciar el simulador, abre una terminal en el directorio principal del proyecto y ejecuta:

```bash
python main.py
```

Aparecerá una ventana de interfaz gráfica dividida en tres secciones:
1. **Panel de Control** (Izquierda): Donde realizarás todas las acciones interactivas.
2. **Vista de Grafos** (Centro): Donde se visualizarán las Máquinas de Mealy del Cajero y el Banco.
3. **Log de Consola** (Derecha): Un registro de todas las transiciones y eventos generados.

---

## 2. Interfaz Principal

### Panel de Control
Aquí encontrarás botones para simular acciones del mundo real:
- **Insertar Tarjeta**: Selecciona una tarjeta del menú desplegable y presiona "Insertar Tarjeta".
- **Teclado Numérico**: Usado para ingresar el PIN de la tarjeta (por defecto `1234` o `4321` dependiendo de la tarjeta), ingresar montos de retiro o nuevas contraseñas.
- **Botones de Acción**:
  - `Retirar Efectivo`
  - `Consultar Saldo`
  - `Cambiar Clave`
  - `Cancelar Operación`

### Vista de Grafos (Máquinas de Mealy)
En el centro se dibujan dos autómatas:
- **Cajero (Azul)**: Representa la interfaz local con el usuario.
- **Banco (Morado)**: Representa el servidor central del banco que realiza las validaciones.

**Cómo interpretarlos**:
- El **nodo verde** indica en qué estado se encuentra la máquina actualmente.
- La **flecha roja/naranja** resalta el último camino tomado (transición).
- Las etiquetas de las flechas tienen el formato `Entrada / Salida`. Por ejemplo, `T / Vt` significa que se recibió la entrada `T` (Insertar Tarjeta) y la máquina emitió una salida `Vt` (Verificar Tarjeta).

### Log de Consola
Muestra el historial en vivo. 
Cada registro sigue este formato:
```text
[CAJERO] q0 --( T: Inserción de tarjeta / Vt: Verificar tarjeta )--> q1: Verificación de estado
[BANCO] p0 --( Vt: Verificar tarjeta / —: — )--> p1: Verificando tarjeta
```

---

## 3. Ejemplo de Uso: Retiro Exitoso

Para hacer un retiro de efectivo correctamente:

1. Selecciona la tarjeta `1234-5678-9012-3456` (con PIN `1234`) y presiona **Insertar Tarjeta**.
2. Verás en el Log cómo las máquinas cambian de estado hasta pedirte la clave.
3. Ingresa el PIN `1234` usando los botones numéricos y dale a **Enter**.
4. Una vez validado, se habilitará el Menú Principal. Haz clic en **Retirar Efectivo**.
5. Ingresa una cantidad, por ejemplo `500` (hay $1500 de saldo disponible) y dale a **Enter**.
6. El Banco validará los fondos y enviará una señal de que todo está bien.
7. El sistema te mostrará un mensaje indicando que retires tus billetes y posteriormente finalizará la operación, expulsando la tarjeta.

---

## 4. Simulando Errores

Puedes forzar diferentes errores para ver cómo se comportan las máquinas de Mealy:
- **Tarjeta Bloqueada**: Selecciona la tarjeta con número final `1111`.
- **Fondos Insuficientes**: Intenta retirar `5000` dólares.
- **Clave Incorrecta (3 intentos)**: Ingresa pines equivocados tres veces seguidas para ver cómo el Cajero transita al estado `q9` (Bloqueo) y el banco rechaza la conexión.
- **Timeout**: Haz clic en el botón manual de Timeout para simular que el tiempo de espera se ha agotado. El Banco revertirá los cambios y el Cajero volverá al inicio.
