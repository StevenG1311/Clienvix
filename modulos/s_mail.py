import json
import smtplib
from pathlib import Path
from email.message import EmailMessage

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config.json"

try:
    with open(CONFIG_PATH, "r", encoding='utf-8') as json_file:
        info = json.load(json_file)

except FileNotFoundError:
    print("Error: Archivo de configuración no encontrado.")
    exit()

class Mensajes:
    def __init__(self):
        # Configuración desde JSON
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

        

