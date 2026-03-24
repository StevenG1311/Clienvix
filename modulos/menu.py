import os
from .core_filter import ApiFilter
from .s_mail import MailConfig
from .conect import user, password

usuario = user()
clave = password()

m = MailConfig()
c = ApiFilter(usuario, clave)

def limpiar():
    os.system("cls") if os.name == "nt" else os.system("clear")

def flujo(label, boton):
    while True:
        limpiar()
        print("-" * 45)
        print(label)
        print("-" * 45)

        for key, (desc, _) in boton.items():
            print(f"[{key}] {desc}")

        print("-" * 45)

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            return None

        accion = boton.get(opcion)

        if accion and accion[1]:
            limpiar()
            print(f">> {accion[0]}\n")
            accion[1]()
        else:
            print("Opción inválida")


def menu_ajustes():
    label = " AJUSTES "
    ajustes = {
        "1": ("Ver Configuración", m.ver_configuracion),
        "2": ("Configurar Correo", m.configurar_mail),
        "3": ("Eliminar Configuración", m.del_config),
        "4":("Cambiar ruta de guardado local", c.new_ruta),
        "0": ("Regresar", None)
    }

    flujo(label, ajustes)

# MENÚ PRINCIPAL
def Menu():
    label = " MENU "
    menu = {
        "1": ("Consultar por Cuenta", c.status_account),
        "2": ("Consultar por Panel", c.status_panel),
        "3": ("Lista de Clientes", c.status_users),
        "4": ("Ajustes", menu_ajustes),
        "0": ("Salir", None)
    }

    flujo(label, menu)
    c.cerrar()
