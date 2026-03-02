from .states import *

# CARGAR / CREAR CONFIGURACIÓN
def cargar_config():
    if not CONFIG_PATH.exists():
        config_default = {
            "MAIL": {
                "NOMBRE": "",
                "CORREO": "",
                "CLAVE": "",
                "SERVER": "",
                "PORT": None,
                "SEGURITY": ""
            }
        }

        CONFIG_PATH.write_text(
            json.dumps(config_default, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        return config_default

    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

def guardar_config():
    try:
        CONFIG_PATH.write_text(
            json.dumps(info, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"Error guardando configuración: {e}")


# Variable global
info = cargar_config()

# VALIDAR SMTP
def validar_smtp(correo, clave, server, puerto, segurity):
    try:
        if segurity == "TLS":
            with smtplib.SMTP(server, puerto, timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(correo, clave)
        else:
            with smtplib.SMTP_SSL(server, puerto, timeout=10) as smtp:
                smtp.login(correo, clave)

        print("✔ Conexión SMTP exitosa")
        return True

    except Exception as e:
        print(f"Error SMTP: {e}")
        return False

# VERIFICAR CONFIG INCOMPLETA
def mail_config_incompleta():
    campos = ["NOMBRE", "CORREO", "CLAVE"]

    for campo in campos:
        valor = info["MAIL"].get(campo)
        if not valor or str(valor).strip() == "":
            return True

    return False

# CONFIGURAR CORREO
def configurar_mail():
    print("\n# Configuración de Correo #\n")

    nombre = input("Nombre: ").strip()
    correo = input("Email: ").strip()
    clave = getpass("Password: ")
    server = input("SMTP Server: ").strip()

    print("\nTipo de seguridad:")
    print("1 - SSL (Puerto 465)")
    print("2 - TLS / STARTTLS (Puerto 587)")

    opcion_seguridad = input("Seleccione: ").strip()

    if opcion_seguridad == "2":
        segurity = "TLS"
        puerto = 587
    else:
        segurity = "SSL"
        puerto = 465

    print("\nValidando conexión SMTP...")

    if not validar_smtp(correo, clave, server, puerto, segurity):
        print("# Error, configuración cancelada. #")
        return

    info["MAIL"] = {
        "NOMBRE": nombre,
        "CORREO": correo,
        "CLAVE": clave,
        "SERVER": server,
        "PORT": puerto,
        "SEGURITY": segurity
    }

    guardar_config()

    print("Configuración guardada correctamente")

# VER CONFIGURACIÓN
def ver_configuracion():
    print("\n...Configuración Actual...\n")

    mail = info.get("MAIL", {})

    print(f"Nombre     : {mail.get('NOMBRE')}")
    print(f"Correo     : {mail.get('CORREO')}")
    print(f"Servidor   : {mail.get('SERVER')}")
    print(f"Puerto     : {mail.get('PORT')}")
    print(f"Seguridad  : {mail.get('SEGURITY')}")


# ==============================
# ELIMINAR CONFIGURACIÓN
# ==============================

def del_config():
    confirm = input("¿Seguro que desea eliminar la configuración? (s/n): ").strip().lower()

    if confirm != "s":
        print("Operación cancelada.")
        return

    info["MAIL"] = {
        "NOMBRE": "",
        "CORREO": "",
        "CLAVE": "",
        "SERVER": "",
        "PORT": None,
        "SEGURITY": ""
    }

    try:
        guardar_config()
        print("✔ Configuración eliminada correctamente.")
    except Exception as e:
        print(f"Error al eliminar configuración: {e}")