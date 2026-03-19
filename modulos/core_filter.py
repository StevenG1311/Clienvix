import os
from .s_mail import *

class ApiFilter:
    def __init__(self):
        self.con = ConectNvx()
        self.mail = Mensajes()
        self.mail_config = MailConfig()

    # FILTRO USUARIOS
    @staticmethod
    def filtrar_usuarios(df):

        print("\nFiltrar usuarios:")
        print("1 - Activos")
        print("2 - Inactivos")
        print("3 - Todos")

        opcion = input("Seleccione: ").strip()

        df = df.copy()
        df["activated"] = df["activated"].astype(str).str.lower()

        if opcion == "1":
            return df[df["activated"].isin(["true", "1"])]

        if opcion == "2":
            return df[df["activated"].isin(["false", "0"])]

        if opcion == "3":
            return df

        print("# Opción inválida #")
        return pd.DataFrame()

    # FILTRO TRACKERS
    @staticmethod
    def filtrar_trackers_offline(df):

        print("\nFiltrar dispositivos offline:")
        print("1 - X días")
        print("2 - X meses")

        opcion = input(">>>: ").strip()

        try:

            if opcion == "1":
                limite = int(input("Cantidad de días: "))

            elif opcion == "2":
                meses = int(input("Cantidad de meses: "))
                limite = meses * 30

            else:
                return pd.DataFrame()

        except ValueError:

            print("# Valor inválido #")
            return pd.DataFrame()

        df = df[df["days_offline"] >= limite]

        return df.sort_values("days_offline", ascending=False)

    # STATUS USERS
    def status_users(self):

        df = self.con.get_users()

        if df.empty:
            print("# No hay usuarios disponibles #")
            return

        df = self.filtrar_usuarios(df)

        if df.empty:
            print("# No hay registros que cumplan el filtro #")
            return

        print(df.to_string(index=True))

        self.export_prompt(df)

    # STATUS PANEL
    def status_panel(self):

        df = self.con.get_trackers()

        if df.empty:
            print("# No hay trackers disponibles #")
            return

        opcion = input("¿Aplicar filtro offline? (s/n): ").lower()

        if opcion == "s":
            df = self.filtrar_trackers_offline(df)

            if df.empty:
                print("# No hay registros #")
                return

        else:

            if "days_offline" in df.columns:
                df = df.drop(columns=["days_offline"])

        print(df.to_string())

        self.export_prompt(df)

    # STATUS ACCOUNT
    def status_account(self):

        cuenta = input("Nombre de la cuenta: ").strip().lower()

        df = self.con.get_trackers()

        if df.empty:
            print("# No hay trackers disponibles #")
            return

        # FILTRO SOLO POR NOMBRE DE CUENTA
        df = df[df["owner_name"].str.lower().str.contains(cuenta, na=False)]

        if df.empty:
            print("# No hay trackers para esa cuenta #")
            return

        opcion = input("¿Aplicar filtro offline? (s/n): ").lower()

        if opcion == "s":

            df = self.filtrar_trackers_offline(df)

            if df.empty:
                print("# No hay registros #")
                return

        else:

            if "days_offline" in df.columns:
                df = df.drop(columns=["days_offline"])

        print(df.to_string())

        self.export_prompt(df)

    # EXPORTACIÓN
    def export_prompt(self, df):

        if input("Exportar (s/n): ").lower() == "s":
            self.export_excel(df)

    def export_excel(self, df):

        archivo = f"Reporte_{datetime.now():%Y%m%d_%H%M}.xlsx"

        print("\n1 - Guardar Localmente")
        print("2 - Enviar por Email")

        opcion = input(">>>: ")

        if opcion == "1":

            ruta = self.mail_config.info.get("RUTA", "")

            if not ruta:
                ruta = input("Ruta (ej: C:/home/user/reportes): ").strip()

                # Guardar en la configuración
                self.mail_config.info["RUTA"] = ruta
                self.mail_config.guardar_config()

            ruta_final = os.path.join(ruta, archivo)

            df.to_excel(ruta_final, index=False)

            print("Archivo guardado:", ruta_final)

        elif opcion == "2":

            df.to_excel(archivo, index=False)

            if self.mail_config.mail_config_incompleta():
                self.mail_config.configurar_mail()

            self.mail.message(archivo)
            self.mail.send()

    def new_ruta(self):
        new = input("Nueva ruta (ej: C:/home/user/reportes): ").strip()
        self.mail_config.info["RUTA"] = new
        self.mail_config.guardar_config()

    def cerrar(self):
        self.con.close()
