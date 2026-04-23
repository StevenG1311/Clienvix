import json
from modulos.connection.conect import password
from modulos.connection.config import j_config, CONFIG_PATH
from modulos.core_data.metodo_estaticos import validar_smtp

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
class MailConfig:
    """Esta clase se encarga de manejar la configuración de correo electrónico,
    incluyendo la visualización, edición y eliminación de la configuración SMTP almacenada en un archivo JSON."""
    def __init__(self):
        self.info = j_config()

    # VER CONFIGURACIÓN ACTUAL ============================================================
    def ver_configuracion(self):
        """Muestra la configuracion actual de correo electrónico almacenada en el archivo JSON."""
        mail = self.info.get("MAIL", {})

        print("<< Configuración Actual >>")
        for key in ["NOMBRE", "CORREO", "SERVER", "PORT", "SECURITY"]:
            print(f"{key:<10}: {mail.get(key)}")

        input("ENTER para continuar...")

    # VERIFICAR CONFIGURACIÓN DE CORREO =======================================================
    def mail_config_incompleta(self):
        """Verifica si hay un correo configurado."""
        mail = self.info.get("MAIL", {})
        return any(not str(mail.get(campo, "")).strip()
                   for campo in ["NOMBRE", "CORREO", "CLAVE"])

    # CONFIGURAR CORREO ============================================================
    def configurar_mail(self):
        """Configura el correo electrónico solicitando al usuario la información necesaria,
        validando la conexión SMTP antes de guardar la configuración en el archivo JSON."""

        print("<< Configuración de Correo >>")

        nombre = input("Nombre: ").strip()
        correo = input("Email: ").strip()
        clave = password()
        server = input("SMTP Server: ").strip()
        opcion = input("1-SSL (465) | 2-TLS (587): ").strip()
        security, puerto = ("TLS", 587) if opcion == "2" else ("SSL", 465)

        if not validar_smtp(correo, clave, server, puerto, security):
            print("<< Error en SMTP >>")
            return

        self.info["MAIL"] = {
            "NOMBRE": nombre,
            "CORREO": correo,
            "CLAVE": clave,
            "SERVER": server,
            "PORT": puerto,
            "SECURITY": security
        }

        self.guardar_config()
        print("<< Configuración guardada >>")

    # GUARDAR CONFIGURACIÓN EN ARCHIVO JSON ==================================================
    def guardar_config(self):
        """Guarda la configuracion en el archivo JSON."""
        CONFIG_PATH.write_text(
            json.dumps(self.info, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

    # ELIMINAR CONFIGURACIÓN ============================================================
    def del_config(self):
        """Elimina la configuracion del correo almacendo en el archivo JSON."""
        if input(">> Eliminar configuración (s/n): ").lower() != "s":
            return

        self.info["MAIL"] = {
            "NOMBRE": "",
            "CORREO": "",
            "CLAVE": "",
            "SERVER": "",
            "PORT": None,
            "SECURITY": ""
        }

        self.guardar_config()
        print("<< Configuración eliminada >>")

   