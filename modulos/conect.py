import sys
import json
import time
import requests
import threading
import pandas as pd
from pathlib import Path
from datetime import datetime
from getpass import getpass
from requests.exceptions import Timeout, RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]

CONFIG_PATH = BASE_DIR / "config.json"

def j_config():
    if not CONFIG_PATH.exists():
        config_default = {
            "MAIL": {
                "NOMBRE": "",
                "CORREO": "",
                "CLAVE": "",
                "SERVER": "",
                "PORT": None,
                "SECURITY": ""
            },
            "URLS": {
                "API": "https://api.navixy.com/v2",
                "PANEL_AUTH": "https://api.navixy.com/v2/panel/account/auth",
                "USER_LIST": "https://api.navixy.com/v2/panel/user/list",
                "USER_HASH": "https://api.navixy.com/v2/panel/user/session/create",
                "TRACKER_LIST": "https://panel.navixy.com/api-v2/panel/tracker/list",
                "TRACKER_STATES":"https://api.navixy.com/v2/tracker/get_states"
            },
            "RUTA": ""
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_default, f, indent=4)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# CLIENTE NAVIXY
class ConectNvx:
    def __init__(self):
        self.config = j_config()

        self.rate_limiter = RateLimiter()

        self.user = input("User: ")
        self.password = getpass("Password: ")

        self.url_panel = self.config["URLS"]["PANEL_AUTH"]
        self.url_user = self.config["URLS"]["USER_LIST"]
        self.url_user_hash = self.config["URLS"]["USER_HASH"]
        self.url_tracker = self.config["URLS"]["TRACKER_LIST"]
        self.url_tracker_states = self.config["URLS"]["TRACKER_STATES"]

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

        df["connection_status"] = df["source"].apply(
            lambda x: x.get("connection_status") if isinstance(x, dict) else None
        )

        columnas = [
            "tracker_id",
            "label",
            "user_id",
            "dealer_id",
            "owner_name",
            "last_connection",
            "connection_status"
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

        network_map = self.get_trackers_network_name(df)
        df["network_name"] = df["tracker_id"].map(network_map)

        columnas_finales = [
            "tracker_id",
            "label",
            "user_id",
            "dealer_id",
            "network_name",
            "owner_name",
            "last_connection",
            "connection_status",
            "days_offline"
        ]

        df = df[columnas_finales]

        return df

    # NETWORK NAME
    def get_trackers_network_name(self, df_trackers: pd.DataFrame) -> dict:

        if df_trackers.empty:
            return {}

        network_map = {}

        # 🔹 obtener usuarios
        df_users = self.get_users()

        if df_users.empty:
            return {tid: None for tid in df_trackers["tracker_id"]}

        # 🔹 usuarios activos
        active_users = set(
            df_users.loc[df_users["activated"] == True, "user_id"]
        )

        # 🔹 agrupar trackers por usuario
        user_groups = {
            user_id: group["tracker_id"].tolist()
            for user_id, group in df_trackers.groupby("user_id")
        }

        with ThreadPoolExecutor(max_workers=10) as executor:

            futures = []

            for user_id, tracker_ids in user_groups.items():

                # usuario inactivo → llenar None
                if user_id not in active_users:
                    for tid in tracker_ids:
                        network_map[tid] = None
                    continue

                futures.append(
                    executor.submit(
                        self._process_user_networks,
                        user_id,
                        tracker_ids
                    )
                )

            for future in as_completed(futures):

                result = future.result()

                if result:
                    network_map.update(result)

        return network_map

    def _process_user_networks(self, user_id: int, tracker_ids: list) -> dict:

        result = {tid: None for tid in tracker_ids}

        payload_user = {
            "hash": self.hash,
            "user_id": int(user_id)
        }

        user_hash_resp = self._post(
            self.url_user_hash,
            payload_user
        )

        if not user_hash_resp:
            return result

        user_hash = user_hash_resp.get("hash")

        if not user_hash:
            return result

        payload_states = {
            "hash": user_hash,
            "tracker_id": tracker_ids
        }

        states_resp = self._post(
            self.url_tracker_states,
            payload_states
        )

        if not states_resp:
            return result

        states = states_resp.get("states", {})

        for tracker_id, tracker_data in states.items():

            gsm = tracker_data.get("gsm")

            if isinstance(gsm, dict):
                result[int(tracker_id)] = gsm.get("network_name")

        return result

    # REQUEST CENTRAL
    def _post(self, url: str, payload: dict, retries=4) -> dict | None:

        for attempt in range(retries):

            try:

                self.rate_limiter.wait()

                response = self.session.post(
                    url,
                    data=payload,
                    timeout=15
                )

                if response.status_code == 429:
                    time.sleep(2 * (attempt + 1))
                    continue

                response.raise_for_status()

                data = response.json()

                if not data.get("success"):

                    status_code = data.get("status", {}).get("code")

                    if status_code == 15:
                        time.sleep(1)
                        continue

                    errores = {
                        3: "Sesión expirada",
                        102: "Usuario o contraseña incorrectos"
                    }

                    raise Exception(
                        errores.get(status_code)
                    )

                return data

            except Timeout:
                print("Timeout: el servidor tarda mucho en responder.")
                time.sleep(1)

            except RequestException as e:
                print(f"Error de conexión: {e}")
                time.sleep(1)

            except Exception as e:
                print(f"Error no capturado: {e}")
                return None

        return None

    # CERRAR SESIÓN
    def close(self):
        self.session.close()
        print("\nSesión cerrada.")
        sys.exit()

class RateLimiter:
    def __init__(self, rate=40, per=1):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        self.lock = threading.Lock()

    def wait(self):

        with self.lock:

            current = time.time()
            time_passed = current - self.last_check
            self.last_check = current

            self.allowance += time_passed * (self.rate / self.per)

            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1:
                sleep_time = (1 - self.allowance) * (self.per / self.rate)
                time.sleep(sleep_time)
                self.allowance = 0
            else:
                self.allowance -= 1