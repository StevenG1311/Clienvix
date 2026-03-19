import smtplib
from .conect import *
from email.message import EmailMessage

class Mensajes:
    def __init__(self):
        # Configuración desde JSON
        info = j_config()
        self.nombre_json = info["MAIL"]["NOMBRE"]
        self.mail_json = info["MAIL"]["CORREO"]
        self.clave_json = info["MAIL"]["CLAVE"]
        self.server_json = info["MAIL"]["SERVER"]
        self.port_json = info["MAIL"]["PORT"]

        # Seguridad configurable (SSL por defecto)
        self.security_json = info["MAIL"].get("SECURITY", "SSL").upper()

        # Variables de estado
        self.msg = None
        self.report_excel = None

    # CREAR MENSAJE #
    def message(self, report_file):
        self.msg = EmailMessage()
        self.msg["From"] = f"{self.nombre_json} <{self.mail_json}>"
        self.msg["To"] = input("to: ")
        self.msg["Cc"] = input("cc: ")
        self.msg["Subject"] = "Reporte!"

        self.report_excel = Path(report_file)

        html = """
        <html>
            <body>
                <p>Reporte de las ultimas actualizaciones. Archivo adjunto.</p>
                <br>
            </body>
        </html>
        """

        self.msg.add_alternative(html, subtype="html")

        with open(self.report_excel, "rb") as report:
            self.msg.add_attachment(
                report.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=self.report_excel.name
            )

    # ENVIAR CORREO (SSL o TLS) #
    def send(self):
        print("Enviando...")

        try:
            if self.security_json == "TLS":
                # STARTTLS (Puerto 587 normalmente)
                with smtplib.SMTP(self.server_json, self.port_json) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login(self.mail_json, self.clave_json)
                    smtp.send_message(self.msg)

            else:
                # SSL directo (Puerto 465 normalmente)
                with smtplib.SMTP_SSL(self.server_json, self.port_json) as smtp:
                    smtp.login(self.mail_json, self.clave_json)
                    smtp.send_message(self.msg)

            print("...Correo enviado...")

            # Eliminar archivo luego de enviar
            self.report_excel.unlink(missing_ok=True)

            return True

        except smtplib.SMTPAuthenticationError:
            print("# Error de autenticación (usuario o contraseña incorrecta) #")
            return False

        except smtplib.SMTPConnectError:
            print("# No se pudo conectar al servidor SMTP #")
            return False

        except smtplib.SMTPException as e:
            print("# Error SMTP #\n", e)
            return False

        except Exception as e:
            print(f"Error inesperado: {e}")
            return False

# ===================================================================================
# CONFIGURAR MAIL
# ===================================================================================
class MailConfig:
    def __init__(self):
        self.info = j_config()

    # VER CONFIGURACION
    def ver_configuracion(self):
        print("...Configuración Actual...")

        mail = self.info.get("MAIL", {})

        print(f"Nombre     : {mail.get('NOMBRE')}")
        print(f"Correo     : {mail.get('CORREO')}")
        print(f"Servidor   : {mail.get('SERVER')}")
        print(f"Puerto     : {mail.get('PORT')}")
        print(f"Seguridad  : {mail.get('SECURITY')}")

        input("\nENTER para continuar...")

    # VERIFICAR CONFIG
    def mail_config_incompleta(self):

        campos = ["NOMBRE", "CORREO", "CLAVE"]

        for campo in campos:
            valor = self.info["MAIL"].get(campo)
            if not valor or str(valor).strip() == "":
                return True

        return False

    # CONFIGURAR MAIL
    def configurar_mail(self):

        print("...Configuración de Correo...")

        nombre = input("Nombre: ").strip()
        correo = input("Email: ").strip()
        clave = password()
        server = input("SMTP Server: ").strip()

        print("\nTipo de seguridad:")
        print("1 - SSL (Puerto 465)")
        print("2 - TLS (Puerto 587)")

        opcion = input("Seleccione: ")

        if opcion == "2":
            security = "TLS"
            puerto = 587
        else:
            security = "SSL"
            puerto = 465

        if not self.validar_smtp(correo, clave, server, puerto, security):
            print("# Error en SMTP #")
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
        print("...Configuración guardada...")
        input("\nENTER para continuar...")

    # GUARDAR CONFIGURACION
    def guardar_config(self):
        CONFIG_PATH.write_text(
            json.dumps(self.info, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

    # ELIMINAR CONFIGURACION
    def del_config(self):
        confirm = input("¿Seguro que desea eliminar la configuración? (s/n): ").lower()

        if confirm != "s":
            print("# Operación cancelada #")
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
        print("...Configuración eliminada...")
        input("\nENTER para continuar...")

    # VALIDAR SMTP
    @staticmethod
    def validar_smtp(correo, clave, server, puerto, security):
        try:
            if security == "TLS":
                with smtplib.SMTP(server, puerto, timeout=10) as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                    smtp.login(correo, clave)

            else:
                with smtplib.SMTP_SSL(server, puerto, timeout=10) as smtp:
                    smtp.login(correo, clave)

            print("...Conexión SMTP exitosa...")
            input("\nENTER para continuar...")
            return True

        except Exception as e:
            print(f"Error SMTP: {e}")
            return False



