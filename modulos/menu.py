from .core_filter import *

m = MailConfig()
c = ApiFilter()

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def pausar():
    input("\nPresione ENTER para continuar...")

def menu_ajustes():
    ajustes = {
        "1": ("Configurar Correo", m.configurar_mail),
        "2": ("Ver Configuración", m.ver_configuracion),
        "3": ("Eliminar Configuración", m.del_config),
        "4":("Cambiar ruta de guardado local", c.new_ruta),
        "0": ("Regresar", None)
    }

    while True:
        limpiar_pantalla()
        print("=== AJUSTES ===")

        for key, (desc, _) in ajustes.items():
            print(f"[{key}] {desc}")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            break

        accion = ajustes.get(opcion)

        if accion and accion[1]:
            limpiar_pantalla()
            accion[1]()
        else:
            print("Opción inválida")

        pausar()

# MENÚ PRINCIPAL
def Menu():
    menu = {
        "1": ("Ver Cuenta", c.status_account),
        "2": ("Ver Panel", c.status_panel),
        "3": ("Lista de Clientes", c.status_users),
        "4": ("Ayustes", menu_ajustes),
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
            c.cerrar()

        accion = menu.get(opcion)

        if accion and accion[1]:
            limpiar_pantalla()
            print(f">>> {accion[0]}\n")
            accion[1]()
        else:
            print("\nOpción inválida.")

        pausar()