import smtplib
from pathlib import Path
from email.message import EmailMessage
from modulos.connection.config import j_config

# ==============================================================================
# SMTP CORE
# ==============================================================================
def _get_smtp_connection(server, port, security):
    """Establece una conexión SMTP utilizando el tipo de seguridad especificado (TLS o SSL)
    y devuelve el objeto de conexión."""
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
    """Envía un correo electrónico utilizando la configuración SMTP proporcionada y el mensaje especificado."""
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
    """Esta clase se encarga de manejar la creación y envío de mensajes de correo electrónico,
    incluyendo la configuración SMTP y la gestión de archivos adjuntos."""
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
        """Crea un mensaje de correo electrónico con un archivo adjunto utilizando la configuración SMTP almacenada."""
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
        """Envía el mensaje de correo electrónico creado previamente utilizando la configuración SMTP almacenada."""
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

