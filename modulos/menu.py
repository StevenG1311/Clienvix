from .edit import *
import os
import sys

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def pausar():
    input("\nPresione ENTER para continuar...")

# MENÚ PRINCIPAL
def Menu():
    if mail_config_incompleta():
        print("Correo no configurado.")
        configurar_mail()

    menu = {
        "1": ("Estado de Cuenta", status_account),
        "2": ("Estado del Panel", status_panel),
        "3": ("Listado de Clientes", status_users),
        "4": ("Configurar Correo", configurar_mail),
        "5": ("Ver Configuración", ver_configuracion),
        "6": ("Eliminar Configuración", del_config),
        "0": ("Salir", None)
    }

    while True:
        limpiar_pantalla()

        print("=" * 45)
        print("        SISTEMA DE GESTIÓN NVX")
        print("=" * 45)

        for key, (descripcion, _) in menu.items():
            print(f"[{key}] {descripcion}")

        print("=" * 45)

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            con.session.close()
            print("\nSesión cerrada.")
            sys.exit()

        accion = menu.get(opcion)

        if accion:
            limpiar_pantalla()
            print(f">>> {accion[0]}\n")
            accion[1]()
        else:
            print("\nOpción inválida.")

        pausar()
