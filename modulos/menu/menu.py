import os
import sys
import time

from modulos.core_data.core_filter import ApiFilter
from modulos.mail.config_mail import MailConfig
from modulos.connection.conect import user, password
from modulos.core_data.exportar_excel import new_ruta

# =======================================================================================
# MENÚ PRINCIPAL Y DE AJUSTES
# =======================================================================================

m = MailConfig()
c = None
SESSION_LABEL = "No hay sesión activa"

# LIMPIAR PANTALLA ============================================================
def limpiar():
    """Limpia la pantalla de la consola."""
    os.system("cls") if os.name == "nt" else os.system("clear")
    
# MANEJO DE SESIÓN ================================================================
def iniciar_sesion():
    """Solicita al usuario que ingrese sus credenciales, intenta iniciar sesión y establece la sesión activa."""
    global c, SESSION_LABEL

    intentos_maximo = 5
    intentos_actuales = 0

    while intentos_actuales < intentos_maximo:
        usuario = user()
        clave = password()

        try:
            c = ApiFilter(usuario, clave)
            SESSION_LABEL = f"Panel {usuario}"
            print("<< Sesión iniciada >>")
            input("ENTER para continuar...")
            return

        except Exception as e:
            intentos_actuales += 1
            intentos_restantes = intentos_maximo - intentos_actuales

            print(f"<< Error: {e} >>")
            if intentos_restantes > 0:
                print(f"<< Quedan {intentos_restantes} intentos >>\n")

                if intentos_restantes < 3:
                    espera = 5 * (3 - intentos_restantes)  # Incrementa el tiempo de espera
                    print("<< Verifica las credenciales >>")
                    
                    for i in range(espera, 0, -1):
                        print(f"\rEspera {i} segundos...", end="")
                        time.sleep(1)
                    print("\n")

            else:
                print("<< Intentos agotados, cerrando programa >>")
                # Solo cerramos si realmente tiene una conexión activa
                if c is not None:
                    c.cerrar()
                sys.exit()

def cambiar_sesion():
    """Permite al usuario cerrar la sesión actual y volver a iniciar sesión con nuevas credenciales."""
    global c, SESSION_LABEL

    if c:
        c.cerrar()

    SESSION_LABEL = "<< Nueva sesión >>"
    print("<< Ingrese credenciales >>")
    iniciar_sesion()

# FLUJO DE MENÚ ===============================================================================
def flujo(label, boton):
    """Maneja el flujo de los menús, mostrando las opciones disponibles
    y ejecutando las acciones correspondientes según la selección del usuario."""
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
            input("ENTER para continuar...")

# MENÚ AJUSTES ===============================================================================
def menu_ajustes():
    """Muestra el menú de ajustes, permitiendo al usuario configurar el correo electrónico,
    eliminar la configuración existente o cambiar la ruta de guardado local para los archivos Excel."""

    label = "<< AJUSTES >>"
    ajustes = {
        "1": ("Ver Configuración", m.ver_configuracion),
        "2": ("Configurar Correo", m.configurar_mail),
        "3": ("Eliminar Configuración", m.del_config),
        "4": ("Cambiar ruta de guardado local", new_ruta),
        "0": ("Regresar", None)
    }

    flujo(label, ajustes)

# MENÚ PRINCIPAL ===============================================================================
def Menu():
    """Inicia el programa mostrando el menú principal, permitiendo al usuario iniciar sesión,
    acceder a las consultas disponibles, configurar ajustes o cambiar de sesión."""
    
    iniciar_sesion()

    label = "<< MENU >>"
    menu = {
        "1": ("Consultar por Cuenta", c.status_account),
        "2": ("Consultar por Panel", c.status_panel),
        "3": ("Lista de Clientes", c.status_users),
        "4": ("Ajustes", menu_ajustes),
        "5": ("Cambiar sesión", cambiar_sesion),
        "0": ("Salir", c.cerrar)
    }

    flujo(label, menu)

    if c:
        c.cerrar()
        sys.exit()