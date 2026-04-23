import pandas as pd
from modulos.connection.conect import ConectNvx
from modulos.mail.s_mail import Mensajes
from modulos.mail.config_mail import MailConfig
from modulos.core_data.exportar_excel import export_prompt
from modulos.core_data.metodo_estaticos import (
    render_dataframe, is_empty,
    filtrar_trackers_offline, filtrar_usuarios
)

class ApiFilter:

    def __init__(self, usuario, clave):
        self.con = ConectNvx(usuario, clave)
        self.mail = Mensajes()
        self.mail_config = MailConfig()

    def status_users(self):
        df = self.con.get_users()
        if is_empty(df): return

        opcion = input("1- Activos | 2- Inactivos | 3- Todos: ")
        df = filtrar_usuarios(df, opcion)

        if is_empty(df): return

        render_dataframe(df, "Usuarios")
        export_prompt(df)

    def status_panel(self):
        df = self.con.get_trackers()
        if is_empty(df): return
        self.procesar_status(df)

    def status_account(self):
        cuenta = input("Cuenta: ").lower()
        df = self.con.get_trackers()

        if is_empty(df): return

        df = df[df["owner_name"].str.lower().str.contains(cuenta, na=False)]
        if is_empty(df): return

        self.procesar_status(df)

    def procesar_status(self, df):
        if is_empty(df): return

        if input("Filtro offline (s/n): ").lower() == "s":
            df = filtrar_trackers_offline(df)
            if is_empty(df): return

        render_dataframe(df)
        export_prompt(df)

    def cerrar(self):
        if self.con:
            self.con.session.close()
            print("\nSession cerrada")