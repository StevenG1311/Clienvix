from datetime import datetime
import os

def export_prompt(df):
    if input("Exportar (s/n): ").lower() == "s":
        export_excel(df)

def export_excel(df):
    from modulos.mail.config_mail import MailConfig
    from modulos.mail.s_mail import Mensajes
    from modulos.core_data.metodo_estaticos import formatear_excel
    from modulos.menu.menu import SESSION_LABEL

    m = MailConfig()
    n = Mensajes()

    archivo = f"Reporte_{SESSION_LABEL}_{datetime.now():%Y%m%d}.xlsx"

    print("1- Local\n2- Email")
    opcion = input(">> ")

    if opcion == "1":
        ruta = m.info.get("RUTA") or input("Ruta: ")
        path = os.path.join(ruta, archivo)

        df.to_excel(path, index=False)
        formatear_excel(path)
        print("Guardado:", path)

    elif opcion == "2":
        df.to_excel(archivo, index=False)
        formatear_excel(archivo)

        if m.mail_config_incompleta():
            m.configurar_mail()

        n.crear_mensaje(archivo)
        n.send()

def new_ruta():
    from modulos.mail.config_mail import MailConfig

    m = MailConfig()

    new = input("Nueva ruta: ").strip()
    m.info["RUTA"] = new
    m.guardar_config()
