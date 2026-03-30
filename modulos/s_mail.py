import json
import smtplib
from email.message import EmailMessage
from pathlib import Path
from .conect import j_config, password, CONFIG_PATH

# ==============================================================================
# SMTP CORE
# ==============================================================================
def _get_smtp_connection(server, port, security):
    if security == "TLS":
        smtp = smtplib.SMTP(server, port)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        return smtp

    elif security == "SSL":
        return smtplib.SMTP_SSL(server, port)

    else:
        raise ValueError("<< Tipo de seguridad inválido >>")

def smtp_send(server, port, mail, clave, security, msg: EmailMessage):
    try:
        with _get_smtp_connection(server, port, security) as smtp:
            smtp.login(mail, clave)
            smtp.send_message(msg)

        return True

    except smtplib.SMTPException as e:
        print(f"<< Error SMTP: {e} >>")
        return False

    except Exception as e:
        print(f"<< Error inesperado: {e} >>")
        return False

# ==============================================================================
# MENSAJES
# ==============================================================================
class Mensajes:
    def __init__(self):
        info = j_config()["MAIL"]
        self.nombre = info["NOMBRE"]
        self.mail = info["CORREO"]
        self.clave = info["CLAVE"]
        self.server = info["SERVER"]
        self.port = info["PORT"]
        self.security = info.get("SECURITY", "SSL").upper()
        self.msg = None
        self.report_excel = None

    # CREAR MENSAJE CON ARCHIVO ADJUNTO ============================================================
    def crear_mensaje(self, report_file):
        msg = EmailMessage()
        msg["From"] = f"{self.nombre} <{self.mail}>"
        msg["To"] = input("To: ").strip()
        msg["Cc"] = input("Cc: ").strip()
        msg["Subject"] = "Reporte!"

        html = """\
        <html>
            <body>
                <p>Reporte de las últimas actualizaciones. Archivo adjunto.</p>
            </body>
        </html>
        """

        msg.add_alternative(html, subtype="html")
        path = Path(report_file)

        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=path.name
            )

        self.msg = msg
        self.report_excel = path

    # ENVIAR MENSAJE ============================================================
    def send(self):
        if not self.msg:
            print("<< No hay mensaje creado >>")
            return False

        print("Enviando...")

        ok = smtp_send(
            self.server,
            self.port,
            self.mail,
            self.clave,
            self.security,
            self.msg
        )

        if ok:
            print("<< Correo enviado >>")
            self.report_excel.unlink(missing_ok=True)

        return ok

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================
class MailConfig:
    def __init__(self):
        self.info = j_config()

    # VER CONFIGURACIÓN ACTUAL ============================================================
    def ver_configuracion(self):
        mail = self.info.get("MAIL", {})

        print("<< Configuración Actual >>")
        for key in ["NOMBRE", "CORREO", "SERVER", "PORT", "SECURITY"]:
            print(f"{key:<10}: {mail.get(key)}")

        input("ENTER para continuar...")

    # VERIFICAR CONFIGURACIÓN DE CORREO =======================================================
    def mail_config_incompleta(self):
        mail = self.info.get("MAIL", {})
        return any(not str(mail.get(campo, "")).strip()
                   for campo in ["NOMBRE", "CORREO", "CLAVE"])

    # CONFIGURAR CORREO ============================================================
    def configurar_mail(self):
        print("<< Configuración de Correo >>")

        nombre = input("Nombre: ").strip()
        correo = input("Email: ").strip()
        clave = password()
        server = input("SMTP Server: ").strip()
        opcion = input("1-SSL (465) | 2-TLS (587): ").strip()
        security, puerto = ("TLS", 587) if opcion == "2" else ("SSL", 465)

        if not self.validar_smtp(correo, clave, server, puerto, security):
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
        CONFIG_PATH.write_text(
            json.dumps(self.info, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

    # ELIMINAR CONFIGURACIÓN ============================================================
    def del_config(self):
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

    # VALIDAR CONFIGURACIÓN SMTP ============================================================
    @staticmethod
    def validar_smtp(correo, clave, server, puerto, security):
        msg = EmailMessage()
        msg["From"] = correo
        msg["To"] = correo
        msg["Subject"] = "Clienvix, mensaje de prueba"
        msg.set_content("Conexión exitosa")

        print("Probando conexión...")
        return smtp_send(server, puerto, correo, clave, security, msg)


