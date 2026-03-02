import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from getpass import getpass
from requests.exceptions import Timeout, RequestException

# CARGAR CONFIGURACIÓN SEGURA
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config.json"

def cargar_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de configuración: {CONFIG_PATH}"
        )

    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

# CLIENTE NAVIXY
class ConectNvx:

    def __init__(self):
        self.config = cargar_config()

        self.user = input("User: ")
        self.password = getpass("Password: ")

        self.url_panel = self.config["URLS"]["PANEL_AUTH"]
        self.url_user = self.config["URLS"]["USER_LIST"]
        self.url_tracker = self.config["URLS"]["TRACKER_LIST"]

        self.session = requests.Session()
        self.hash = self._login()

    # LOGIN
    def _login(self) -> str:
        payload = {
            "login": self.user,
            "password": self.password
        }

        response = self._post(self.url_panel, payload)

        if not response:
            raise SystemExit("No se pudo autenticar.")

        hash_value = response.get("hash")

        if not hash_value:
            raise Exception("No se recibió hash de autenticación.")

        return hash_value

    # USUARIOS
    def get_users(self) -> pd.DataFrame:
        payload = {"hash": self.hash}
        response = self._post(self.url_user, payload)

        if not response:
            return pd.DataFrame()

        users = response.get("list", [])
        if not users:
            return pd.DataFrame()

        df = pd.DataFrame(users)
        df.rename(columns={"id": "user_id"}, inplace=True)

        columnas = [
            "user_id",
            "dealer_id",
            "activated",
            "login",
            "first_name",
            "last_name",
            "legal_name"
        ]

        df = df[columnas]
        df.reset_index(drop=True, inplace=True)

        return df

    # TRACKERS
    def get_trackers(self) -> pd.DataFrame:
        payload = {"hash": self.hash}
        response = self._post(self.url_tracker, payload)

        if not response:
            return pd.DataFrame()

        trackers = response.get("list", [])
        if not trackers:
            return pd.DataFrame()

        df = pd.DataFrame(trackers)
        df.rename(columns={"id": "tracker_id"}, inplace=True)

        columnas = [
            "tracker_id",
            "label",
            "user_id",
            "dealer_id",
            "owner_name",
            "last_connection"
        ]

        df = df[columnas]

        df["last_connection"] = pd.to_datetime(
            df["last_connection"],
            errors="coerce"
        )

        df["days_offline"] = (
            datetime.now() - df["last_connection"]
        ).dt.days

        df["days_offline"] = df["days_offline"].fillna(0).astype(int)
        df.reset_index(drop=True, inplace=True)

        return df

    # REQUEST CENTRAL
    def _post(self, url: str, payload: dict) -> dict | None:
        try:
            response = self.session.post(
                url,
                data=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                status_code = data.get("status", {}).get("code")

                errores = {
                    3: "Sesión expirada",
                    15: "Rate limit superado",
                    102: "Usuario o contraseña incorrectos"
                }

                raise Exception(
                    errores.get(status_code, "Error desconocido API")
                )

            return data

        except Timeout:
            print("Timeout: el servidor tarda mucho en responder.")
            return None

        except RequestException as e:
            print(f"Error de conexión: {e}")
            return None

        except Exception as e:
            print(f"Error no capturado: {e}")
            return None

    # CERRAR SESIÓN
    def close(self):
        self.session.close()