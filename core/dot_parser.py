"""
dot_parser.py — Parser dinámico de formato DOT para Máquinas de Mealy.

Parsea strings en formato DOT (Graphviz) y extrae:
- Estados (nodos)
- Estado inicial (doble círculo)
- Transiciones con etiquetas "entrada / salida"

Retorna los datos necesarios para construir una MealyMachine.
"""

import re
from typing import Optional


def parsear_dot(cadena_dot: str) -> dict:
    """
    Parsea una cadena en formato DOT y extrae la definición
    de una Máquina de Mealy.

    Args:
        cadena_dot: String con el contenido del archivo DOT.

    Returns:
        Diccionario con:
            - 'estados': set de nombres de estados
            - 'estado_inicial': nombre del estado inicial
            - 'transiciones': dict de (estado, entrada) -> (nuevo_estado, salida)
            - 'alfabeto_entrada': set de símbolos de entrada
            - 'alfabeto_salida': set de símbolos de salida
    """
    estados = set()
    estado_inicial = None
    transiciones = {}
    alfabeto_entrada = set()
    alfabeto_salida = set()

    # Extraer estado inicial (doble círculo)
    # Busca: node [shape = doublecircle]; q0;
    patron_inicial = re.compile(
        r'node\s*\[\s*shape\s*=\s*doublecircle\s*\]\s*;\s*(\w+)\s*;'
    )
    match_inicial = patron_inicial.search(cadena_dot)
    if match_inicial:
        estado_inicial = match_inicial.group(1)
        estados.add(estado_inicial)

    # Extraer transiciones
    # Busca: q0 -> q1 [label = "T / Vt"];
    # También maneja labels sin salida: q1 -> q2 [label = "Ch"];
    patron_transicion = re.compile(
        r'(\w+)\s*->\s*(\w+)\s*\[\s*label\s*=\s*"([^"]+)"\s*\]'
    )

    for match in patron_transicion.finditer(cadena_dot):
        estado_origen = match.group(1)
        estado_destino = match.group(2)
        etiqueta = match.group(3).strip()

        # Ignorar nodos especiales (start, point)
        if estado_origen in ('start',):
            if estado_inicial is None:
                estado_inicial = estado_destino
            estados.add(estado_destino)
            continue

        estados.add(estado_origen)
        estados.add(estado_destino)

        # Parsear la etiqueta: "entrada / salida" o "entrada"
        entrada, salida = _parsear_etiqueta(etiqueta)

        alfabeto_entrada.add(entrada)
        if salida:
            alfabeto_salida.add(salida)

        # Registrar la transición
        clave = (estado_origen, entrada)
        transiciones[clave] = (estado_destino, salida)

    # Verificar que encontramos un estado inicial
    if estado_inicial is None:
        raise ValueError("No se encontró un estado inicial en el DOT.")

    return {
        'estados': estados,
        'estado_inicial': estado_inicial,
        'transiciones': transiciones,
        'alfabeto_entrada': alfabeto_entrada,
        'alfabeto_salida': alfabeto_salida,
    }


def _parsear_etiqueta(etiqueta: str) -> tuple[str, Optional[str]]:
    """
    Parsea una etiqueta de transición DOT.

    Formatos soportados:
        - "entrada / salida"  → ("entrada", "salida")
        - "entrada/salida"    → ("entrada", "salida")
        - "entrada"           → ("entrada", None)
        - "epsilon / salida"  → ("epsilon", "salida")

    Args:
        etiqueta: String con la etiqueta de la transición.

    Returns:
        Tupla (entrada, salida). salida puede ser None si no hay.
    """
    if '/' in etiqueta:
        partes = etiqueta.split('/')
        entrada = partes[0].strip()
        salida = partes[1].strip() if len(partes) > 1 else None
        # Manejar salida vacía
        if salida == '':
            salida = None
        return entrada, salida
    else:
        return etiqueta.strip(), None


def cargar_dot_desde_archivo(ruta: str) -> dict:
    """
    Carga un archivo DOT y lo parsea.

    Args:
        ruta: Ruta al archivo .dot

    Returns:
        Diccionario con la definición de la máquina.
    """
    with open(ruta, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()
    return parsear_dot(contenido)
