# ATM-Bank System

Este proyecto es una simulación de un sistema distribuido de Cajero Automático (ATM) y Banco, modelado estrictamente a través de dos **Máquinas de Mealy** que se comunican entre sí.

## Arquitectura del Sistema

El sistema ha sido diseñado utilizando principios de *Clean Architecture*, separando claramente las responsabilidades en distintas capas:

- **Core (Lógica de Autómatas)**: Implementación pura de las Máquinas de Mealy. Analiza dinámicamente archivos en formato DOT para cargar estados y transiciones.
- **Controllers (Capa de Comunicación)**: Encargada de gestionar la comunicación asíncrona mediante paso de mensajes entre la máquina del Cajero y la máquina del Banco. También diferencia entre "mensajes de red" (a enviar a la otra máquina) y "acciones locales" (ej. mostrar errores, dispensar billetes).
- **GUI (Capa de Presentación)**: Interfaz interactiva desarrollada en Python con `customtkinter`. Renderiza visualmente los grafos de estados utilizando `networkx` y `matplotlib`.

## Estructura del Proyecto

```text
ATM-Bank/
├── controllers/    # Controladores de comunicación (Dispatcher)
├── core/           # Lógica pura de Autómatas (Máquinas de Mealy)
├── gui/            # Interfaz gráfica (Tkinter/CustomTkinter)
├── machines/       # Archivos de definición de los autómatas en formato DOT
├── main.py         # Punto de entrada de la aplicación
├── requirements.txt# Dependencias del proyecto
└── README.md       # Este archivo
```

## Requisitos Previos

Para ejecutar el proyecto, asegúrate de tener instalado Python 3.8 o superior y las siguientes dependencias:

- `customtkinter>=5.2.0`
- `networkx>=3.0`
- `matplotlib>=3.7.0`

Puedes instalar las dependencias ejecutando:

```bash
pip install -r requirements.txt
```

## Ejecución

Para iniciar el simulador, simplemente ejecuta el archivo `main.py` desde la raíz del proyecto:

```bash
python main.py
```

## Características de la Interfaz

- **Panel de Control**: Botones interactivos para simular acciones del usuario en el cajero (inserción de tarjeta, PIN, selección de operación).
- **Visualización en Tiempo Real**: Renderizado en vivo de los diagramas de estados (Cajero y Banco). El estado activo se resalta visualmente tras cada transición.
- **Consola de Eventos**: Log detallado mostrando el historial de transiciones (Estado Origen -> Entrada / Salida -> Estado Destino) para facilitar el monitoreo del sistema.