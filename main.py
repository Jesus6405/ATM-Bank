"""
main.py — Punto de entrada del sistema ATM-Bank.

Carga las Máquinas de Mealy desde archivos DOT,
inicializa el despachador y lanza la GUI.
"""

import os
import sys

# Agregar el directorio raíz al path
directorio_raiz = os.path.dirname(os.path.abspath(__file__))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

from gui.app import AplicacionATM


def main():
    """Función principal de la aplicación."""

    # Rutas a los archivos DOT
    ruta_cajero = os.path.join(directorio_raiz, 'machines', 'cajero.dot')
    ruta_banco = os.path.join(directorio_raiz, 'machines', 'banco.dot')

    # Verificar que los archivos existen
    if not os.path.exists(ruta_cajero):
        print(f"❌ Error: No se encontró el archivo {ruta_cajero}")
        sys.exit(1)
    if not os.path.exists(ruta_banco):
        print(f"❌ Error: No se encontró el archivo {ruta_banco}")
        sys.exit(1)

    print("🏧 Iniciando sistema ATM-Bank...")
    print(f"📂 Cargando cajero: {ruta_cajero}")
    print(f"📂 Cargando banco: {ruta_banco}")

    # Crear y ejecutar la aplicación
    app = AplicacionATM(ruta_cajero, ruta_banco)
    app.mainloop()


if __name__ == '__main__':
    main()
