import os
import pandas as pd
from datetime import datetime
from .conect import ConectNvx
from .s_mail import Mensajes, MailConfig

class ApiFilter:
    def __init__(self, usuario, clave):
        self.con = ConectNvx(usuario, clave)
        self.mail = Mensajes()
        self.mail_config = MailConfig()

    # FILTRO USUARIOS
    @staticmethod
    def filtrar_usuarios(df):
        print("<< Filtrar usuarios >>")
        d = ("Activos", "Inactivos", "Todos")

        for i in range(3):
            print(f"{i + 1}- {d[i]}")

        opcion = input(">>: ").strip()

        df = df.copy()
        df["activated"] = df["activated"].astype(str).str.lower()

        if opcion == "1":
            return df[df["activated"].isin(["true", "1"])]

        if opcion == "2":
            return df[df["activated"].isin(["false", "0"])]

        if opcion == "3":
            return df

        print("<< Opción inválida >>")
        return pd.DataFrame()

    # FILTRO TRACKERS
    @staticmethod
    def filtrar_trackers_offline(df):

        print("<< Filtrar dias offline >>")
        d = ("Por dias", "Por mes")

        for i in range(2):
            print(f"{i + 1}- {d[i]}")

        opcion = input(">>: ").strip()

        try:

            if opcion == "1":
                limite = int(input(">> Cantidad de días: "))

            elif opcion == "2":
                meses = int(input(">> Cantidad de meses: "))
                limite = meses * 30

            else:
                return pd.DataFrame()

        except ValueError:

            print("<< Valor inválido >>")
            return pd.DataFrame()

        df = df[df["days_offline"] >= limite]

        return df.sort_values("days_offline", ascending=False)

    def procesar_status(self,df: pd.DataFrame):
        if df.empty:
            print("<< No hay registros >>")
            return

        opcion = input(">> Filtro offline (s/n)?: ").lower()

        if opcion == "s":
            df = self.filtrar_trackers_offline(df)

            if df.empty:
                print("<< No hay registros >>")
                return
        else:
            if "days_offline" in df.columns:
                df = df.drop(columns=["days_offline"])

        print(df.to_string())
        self.export_prompt(df)

    # STATUS USERS
    def status_users(self):
        df = self.con.get_users()

        if df.empty:
            print("<< No hay usuarios disponibles >>")
            return

        df = self.filtrar_usuarios(df)

        if df.empty:
            print("<< No hay registros que cumplan el filtro >>")
            return

        print(df.to_string(index=True))

        self.export_prompt(df)

    # STATUS PANEL
    def status_panel(self):
        df = self.con.get_trackers()

        if df.empty:
            print("<< No hay trackers disponibles >>")
            return

        self.procesar_status(df)

    # STATUS ACCOUNT
    def status_account(self):
        cuenta = input(">> Nombre de la cuenta: ").strip().lower()

        df = self.con.get_trackers()

        if df.empty:
            print("<< No hay trackers disponibles >>")
            return

        df = df[df["owner_name"].str.lower().str.contains(cuenta, na=False)]

        if df.empty:
            print("<< No hay trackers para esa cuenta >>")
            return

        self.procesar_status(df)

    # EXPORTACIÓN
    def export_prompt(self, df):

        if input(">> Exportar (s/n): ").lower() == "s":
            self.export_excel(df)

    def export_excel(self, df):

        import re

        def limpiar_valor(valor):
            if isinstance(valor, str):
                return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', valor)
            return valor

        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].map(limpiar_valor)

        archivo = f"Reporte_{datetime.now():%Y%m%d_%H%M}.xlsx"

        print("<< Guardar archivo >>")
        d = ("Local", "Enviar por correo")

        for i in range(2):
            print(f"{i + 1}- {d[i]}")

        opcion = input(">>: ")

        if opcion == "1":

            ruta = self.mail_config.info.get("RUTA", "")

            if not ruta:
                ruta = input("Ruta (ej: C:/home/user/reportes): ").strip()

                # Guardar en la configuración
                self.mail_config.info["RUTA"] = ruta
                self.mail_config.guardar_config()

            ruta_final = os.path.join(ruta, archivo)

            df.to_excel(ruta_final, index=False)

            print(f"<< Archivo guardado: {ruta_final} >>")

        elif opcion == "2":

            df.to_excel(archivo, index=False)

            if self.mail_config.mail_config_incompleta():
                self.mail_config.configurar_mail()

            self.mail.crear_mensaje(archivo)
            self.mail.send()
            input("ENTER para continuar...")

    def new_ruta(self):
        new = input("Nueva ruta (ej: C:/home/user/reportes): ").strip()
        self.mail_config.info["RUTA"] = new
        self.mail_config.guardar_config()

    def cerrar(self):
        self.con.close()
