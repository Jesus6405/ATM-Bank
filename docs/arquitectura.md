# Arquitectura del Sistema ATM-Bank

El sistema ATM-Bank es una simulación interactiva de un entorno distribuido en el que un Cajero Automático (ATM) y un Banco interactúan a través del intercambio de mensajes. El núcleo lógico de ambas entidades se basa en **Máquinas de Mealy**.

El sistema ha sido estructurado siguiendo principios de *Clean Architecture* para separar la lógica de negocio, la comunicación y la interfaz de usuario.

---

## 1. Diseño y Capas del Sistema

La aplicación está dividida en tres capas principales:

### 1.1 Capa Core (Lógica de Autómatas)
Ubicación: `core/`

El *Core* del sistema es responsable de simular el comportamiento de las entidades como Máquinas de Mealy.
- **`mealy_machine.py`**: Implementa la clase `MaquinaMealy`. Su responsabilidad es procesar entradas, buscar la transición válida correspondiente, cambiar de estado y generar una salida (si existe). Es agnóstica de la GUI y de la red.
- **`dot_parser.py`**: Parsea archivos `.dot` (Graphviz) generados externamente, los cuales definen los grafos del Cajero y el Banco. Extrae los estados, alfabetos y transiciones para instanciar las Máquinas de Mealy de manera dinámica.

### 1.2 Capa de Control (Comunicación)
Ubicación: `controllers/`

Esta capa actúa como puente entre el usuario, el core y el servidor del banco, simulando un entorno de red.
- **`dispatcher.py`**: Es el cerebro de la comunicación.
  - Recibe símbolos (eventos) generados por el usuario o por las máquinas.
  - Determina si un símbolo de salida de una máquina es un "mensaje de red" o una "acción local".
  - Si es un **mensaje de red** (ej. *Verificar Tarjeta `Vt`* enviado por el Cajero al Banco), el dispatcher lo enruta como una entrada hacia la máquina del Banco.
  - Sincroniza y orquesta el flujo bidireccional asíncrono entre ambos autómatas.
- **`bank_data.py`**: Base de datos simulada en memoria. El Banco consulta esta capa para verificar si una tarjeta existe, si un PIN es válido y si hay fondos suficientes para un retiro.

### 1.3 Capa de Presentación (GUI)
Ubicación: `gui/`

Proporciona la interfaz interactiva basada en `customtkinter`.
- **`app.py`**: Contenedor principal que ensambla todos los módulos gráficos y los conecta al `Despachador`.
- **`control_panel.py`**: Interfaz donde el usuario realiza acciones (insertar tarjeta, ingresar PIN, retirar efectivo). Estas acciones se traducen en símbolos del alfabeto de entrada y se envían al `Despachador`.
- **`graph_view.py`**: Visualizador en tiempo real de los grafos de la Máquina de Mealy. Utiliza `networkx` y `matplotlib` para dibujar los grafos leídos de los archivos DOT, coloreando de forma dinámica el estado activo de cada máquina y resaltando la última transición realizada.

---

## 2. Flujo de Comunicación (Simulación de Red)

Al estar basado en Máquinas de Mealy, la comunicación sigue este flujo:
1. **Estímulo**: El usuario presiona un botón (ej. Insertar Tarjeta).
2. **Entrada al Autómata A**: Se inyecta la entrada `T` a la máquina del Cajero.
3. **Transición y Salida**: El Cajero procesa la transición (ej. Estado $q_0 \rightarrow q_1$) y genera una salida (ej. `Vt` - Verificar Tarjeta).
4. **Despachador (Red)**: El dispatcher capta la salida `Vt`. Reconoce que `Vt` pertenece a los *símbolos de red* y que su destinatario es el Banco.
5. **Entrada al Autómata B**: El dispatcher inyecta la entrada `Vt` a la máquina del Banco.
6. **Lógica Interna**: El Banco entra a su estado de verificación ($p_1$), consulta `bank_data.py` y, tras procesarlo, envía de forma automática otra salida (ej. `Ce` - Conexión establecida o `Cr` - Conexión rechazada) hacia el Cajero.

Este ciclo de retroalimentación se repite hasta que el usuario retira su tarjeta.

---

## 3. Extensibilidad

El sistema es altamente modular y extensible:
- **Nuevas Reglas de Negocio**: Basta con modificar los archivos `.dot` en la carpeta `machines/` para agregar nuevos estados o transiciones. No es necesario modificar el *Core* ni la lógica de visualización de los grafos.
- **Nuevos Mensajes de Red**: Para añadir una nueva operación (ej. Depósitos), se añade la transición al grafo y se actualizan los diccionarios de alfabetos en `machine_config.py`.
