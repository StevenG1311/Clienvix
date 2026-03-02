from .conect import *
from .s_mail import *

con = ConectNvx()
msm = Mensajes()

# FILTRO USUARIOS #
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

    elif opcion == "2":
        return df[df["activated"].isin(["false", "0"])]

    elif opcion == "3":
        return df

    else:
        print("# Opción inválida #")
        return pd.DataFrame()

# FILTRO TRACKERS OFFLINE #
def filtrar_trackers_offline(df):
    print("\nFiltrar dispositivos offline:")
    print("1 - Más de X días")
    print("2 - Más de X meses")

    opcion = input(">: ").strip()

    try:
        if opcion == "1":
            limite = int(input("Cantidad de días: ").strip())
        elif opcion == "2":
            meses = int(input("Cantidad de meses: ").strip())
            limite = meses * 30
        else:
            return pd.DataFrame()
    except ValueError:
        print("# Valor inválido #")
        return pd.DataFrame()

    df = df.copy()

    # Ya viene calculado desde el cliente
    df = df[df["days_offline"] >= limite]

    return df.sort_values("days_offline", ascending=False)

# STATUS USERS #
def status_users():
    df = con.get_users()

    if df.empty:
        print("# No hay usuarios disponibles #")
        return

    df_filtrado = filtrar_usuarios(df)

    if df_filtrado.empty:
        print("# No hay registros que cumplan el filtro #")
        return

    df_filtrado.reset_index(drop=True, inplace=True)

    print("\n" + "=" * 70)
    print("LISTA DE CLIENTES".center(70))
    print("=" * 70)

    print(df_filtrado.to_string(index=True))
    print(f"\nTotal: {len(df_filtrado)} registros\n")

    export_prompt(df_filtrado)

# STATUS PANEL #
def status_panel():
    df = con.get_trackers()

    if df.empty:
        print("# No hay trackers disponibles #")
        return

    opcion = input("¿Aplicar filtro de días offline? (s/n): ").strip().lower()

    if opcion == "s":
        df = filtrar_trackers_offline(df)

        if df.empty:
            print("# No hay registros que cumplan el filtro #")
            return
    else:
        # 🔹 Si NO quiere filtro, quitamos la columna days_offline
        if "days_offline" in df.columns:
            df = df.drop(columns=["days_offline"])

    df.reset_index(drop=True, inplace=True)

    print("\n" + "=" * 70)
    print("TRACKERS DEL PANEL".center(70))
    print("=" * 70)

    print(df.to_string(index=True))
    print(f"\nTotal: {len(df)} registros\n")

    export_prompt(df)
# STATUS ACCOUNT #
def status_account():
    account_name = input("Ingrese el nombre exacto de la cuenta: ").strip().lower()

    df = con.get_trackers()

    if df.empty:
        print("# No hay trackers disponibles #")
        return

    # 🔹 Filtrar SOLO por nombre de cuenta
    df_account = df[df["owner_name"].astype(str).str.strip().str.lower() == account_name].copy()

    if df_account.empty:
        print("# No se encontraron registros para esa cuenta #")
        return

    opcion = input("¿Aplicar filtro de días offline? (s/n): ").strip().lower()

    if opcion == "s":
        df_final = filtrar_trackers_offline(df_account)

        if df_final.empty:
            print("# No hay registros offline para esa cuenta #")
            return
    else:
        # 🔹 Si NO quiere filtro, eliminamos la columna days_offline
        df_final = df_account.copy()

        if "days_offline" in df_final.columns:
            df_final = df_final.drop(columns=["days_offline"])

    df_final.reset_index(drop=True, inplace=True)

    print("\n" + "=" * 70)
    print(f"DISPOSITIVOS EN CUENTA: {account_name}".center(70))
    print("=" * 70)

    print(df_final.to_string(index=True))
    print(f"\nTotal: {len(df_final)} registros\n")

    export_prompt(df_final)

# EXPORTACIÓN #
def export_prompt(df):
    if input("Exportar (yes/no): ").strip().lower() == "yes":
        export_excel(df)

def export_excel(df):
    archivo = f"Reporte_{datetime.now():%Y%m%d_%H%M}.xlsx"

    try:
        print("\n1 - Guardar Localmente")
        print("2 - Enviar por Email")
        opcion = input(">: ").strip()

        if opcion == "1":
            import os
            ruta = input("Ingrese ruta (ej: C:/Reportes/): ").strip()
            ruta_final = os.path.join(ruta, archivo)
            df.to_excel(ruta_final, index=False)
            print(f"\n[OK] Archivo guardado en: {ruta_final}\n")

        elif opcion == "2":
            df.to_excel(archivo, index=False)
            msm.message(archivo)
            msm.send()

    except Exception as e:
        print(f"# Error al exportar: {e} #")