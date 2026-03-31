import os
import sys
from .core_filter import ApiFilter
from .s_mail import MailConfig
from .conect import user, password

# =======================================================================================
# MENÚ PRINCIPAL Y DE AJUSTES
# =======================================================================================

m = MailConfig()
c = None  # Control de sesión
SESSION_LABEL = "No hay sesión activa"

# LIMPIAR PANTALLA ============================================================
def limpiar():
    '''Limpia la pantalla de la consola de forma compatible con Windows y Linux.'''
    os.system("cls") if os.name == "nt" else os.system("clear")

# MANEJO DE SESIÓN ================================================================
def iniciar_sesion():
    '''Solicita al usuario que ingrese sus credenciales, intenta iniciar sesión y establece la sesión activa.'''
    global c, SESSION_LABEL

    usuario = user()
    clave = password()

    try:
        c = ApiFilter(usuario, clave)
        SESSION_LABEL = f"Panel {usuario}"
        print("<< Sesión iniciada >>")

    except Exception as e:
        print(f"<< {e} >>")
        sys.exit()

    input("Presione ENTER para continuar...")

def cambiar_sesion():
    ''''Permite al usuario cerrar la sesión actual y volver a iniciar sesión con nuevas credenciales.'''
    global c, SESSION_LABEL

    if c:
        c.cerrar()

    SESSION_LABEL = "<< Nueva sesión >>"
    print("<< Ingrese credenciales >>")
    iniciar_sesion()

# FLUJO DE MENÚ ===============================================================================
def flujo(label, boton):
    '''Maneja el flujo de los menús, mostrando las opciones disponibles 
    y ejecutando las acciones correspondientes según la selección del usuario.'''
    while True:
        limpiar()
        print("-" * 45)
        print(label)
        print("-" * 45)
        print(SESSION_LABEL) 
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
            print("<< Opción inválida >>")
            input("Presione ENTER para continuar...")

# MENÚ AJUSTES ===============================================================================
def menu_ajustes():
    '''Muestra el menú de ajustes, permitiendo al usuario configurar el correo electrónico,
    eliminar la configuración existente o cambiar la ruta de guardado local para los archivos Excel.'''

    label = "<< AJUSTES >>"
    ajustes = {
        "1": ("Ver Configuración", m.ver_configuracion),
        "2": ("Configurar Correo", m.configurar_mail),
        "3": ("Eliminar Configuración", m.del_config),
        "4": ("Cambiar ruta de guardado local", lambda: c.new_ruta() if c else print("Debe iniciar sesión primero")),
        "0": ("Regresar", None)
    }

    flujo(label, ajustes)

# MENÚ PRINCIPAL ===============================================================================
def Menu():
    '''Inicia el programa mostrando el menú principal, permitiendo al usuario iniciar sesión, 
    acceder a las consultas disponibles, configurar ajustes o cambiar de sesión.'''
    
    iniciar_sesion()

    label = "<< MENU >>"
    menu = {
        "1": ("Consultar por Cuenta", lambda: c.status_account() if c else print("Debe iniciar sesión")),
        "2": ("Consultar por Panel", lambda: c.status_panel() if c else print("Debe iniciar sesión")),
        "3": ("Lista de Clientes", lambda: c.status_users() if c else print("Debe iniciar sesión")),
        "4": ("Ajustes", menu_ajustes),
        "5": ("Cambiar sesión", cambiar_sesion),
        "0": ("Salir", None)
    }

    flujo(label, menu)

    if c:
        c.cerrar()
        sys.exit()