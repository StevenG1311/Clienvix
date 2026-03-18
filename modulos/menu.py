from .core_filter import *

m = MailConfig()
c = ApiFilter()

def menu_ajustes():
    ajustes = {
        "1": ("Configurar Correo", m.configurar_mail),
        "2": ("Ver Configuración", m.ver_configuracion),
        "3": ("Eliminar Configuración", m.del_config),
        "4":("Cambiar ruta de guardado local", c.new_ruta),
        "0": ("Regresar", None)
    }

    while True:
        print("-" * 45)
        print(" AJUSTES ")
        print("-" * 45)

        for key, (desc, _) in ajustes.items():
            print(f"[{key}] {desc}")

        print("-" * 45)

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            break

        accion = ajustes.get(opcion)

        if accion and accion[1]:
            print(f">>> {accion[0]}\n")
            accion[1]()
        else:
            print("Opción inválida")

# MENÚ PRINCIPAL
def Menu():
    menu = {
        "1": ("Consultar Cuenta", c.status_account),
        "2": ("Consultar Panel", c.status_panel),
        "3": ("Lista de Clientes", c.status_users),
        "4": ("Ajustes", menu_ajustes),
        "0": ("Salir", None)
    }

    while True:
        print("-" * 45)
        print(" MENU ")
        print("-" * 45)

        for key, (descripcion, _) in menu.items():
            print(f"[{key}] {descripcion}")

        print("-" * 45)

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            c.cerrar()

        accion = menu.get(opcion)

        if accion and accion[1]:
            print(f">>> {accion[0]}\n")
            accion[1]()
        else:
            print("\nOpción inválida.")
