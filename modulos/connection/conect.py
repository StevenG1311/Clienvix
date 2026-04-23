import sys
import pwinput
import requests
import pandas as pd

from tqdm import tqdm
from datetime import datetime
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
from .ratelimiter import RateLimiter
from .config import j_config

# FUNCIONES DE ENTRADA DE USUARIO & PASSWORD ============================================================
def user():
    usuario = input("User: ")
    return usuario

def password():
    if sys.stdin.isatty():
        clave = pwinput.pwinput("Password: ", mask='*')
    else:
        clave = getpass("Password: ")

    return clave

# =========================================================================================================
# CLIENTE NAVIXY
# =========================================================================================================
class ConectNvx:
    """Esta clase se encarga de manejar la conexión con NAVIXY, incluyendo autenticación,
    obtención de datos de usuarios y trackers, y control de tasa para evitar exceder los límites del API."""
    def __init__(self, usuario, clave):
        self.config = j_config()
        self.rate_limiter = RateLimiter()

        self.user = usuario
        self.password = clave

        self.url_panel = self.config["URLS"]["PANEL_AUTH"]
        self.url_user = self.config["URLS"]["USER_LIST"]
        self.url_user_hash = self.config["URLS"]["USER_HASH"]
        self.url_tracker = self.config["URLS"]["TRACKER_LIST"]
        self.url_tracker_states = self.config["URLS"]["TRACKER_STATES"]

        self.session = requests.Session()
        self.hash = self._login()

    # LOGIN ==============================================================================================
    def _login(self) -> str:
        """Se conecta a NAVIXY utilizando las credenciales proporcionadas
        y obtiene un token de autenticación (hash) para futuras solicitudes."""
        payload = {
            "login": self.user,
            "password": self.password
        }

        response = self._post(self.url_panel, payload)

        # Validar tipo de respuesta
        if not isinstance(response, dict):
            raise Exception("Respuesta del servidor no es válida")

        # Validar autenticación
        if not response.get("success", False):
            error_msg = (
                response.get("status", {})
                    .get("description")
            )
            self.session.close()
            raise Exception(error_msg)
            
        # Retornar token/hash (ajusta según tu API)
        return response.get("hash")
    
    def end(self):
        if self.session:
            self.session.close()
    
    # OBTENER USUARIOS ===================================================================================
    def get_users(self) -> pd.DataFrame:
        """Obtiene la lista de usuarios desde NAVIXY y devuelve un DataFrame con la información relevante."""
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

    # OBTENER TRACKERS ====================================================================================
    def get_trackers(self) -> pd.DataFrame:
        """Obtiene la lista de trackers desde NAVIXY y devuelve un DataFrame con la información relevante."""
        payload = {"hash": self.hash}
        response = self._post(self.url_tracker, payload)

        if not response:
            return pd.DataFrame()

        trackers = response.get("list", [])
        if not trackers:
            return pd.DataFrame()

        df = pd.DataFrame(trackers)
        df.rename(columns={"id": "tracker_id"}, inplace=True)

        df[["connection_status", "phone", "model", "device_id"]] = df["source"].apply(
            lambda x: pd.Series({
                "connection_status": x.get("connection_status") if isinstance(x, dict) else None,
                "phone": x.get("phone") if isinstance(x, dict) else None,
                "model":x.get("model") if isinstance(x, dict) else None,
                "device_id": x.get("device_id") if isinstance(x, dict) else None
            })
        )

        columnas = [
            "tracker_id",
            "label",
            "user_id",
            "dealer_id",
            "owner_name",
            "phone",
            "model",
            "device_id",
            "connection_status",
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

        network_map = self.get_trackers_network_name(df)
        df["network_name"] = df["tracker_id"].map(network_map)

        columnas_finales = [
            "tracker_id",
            "label",
            "user_id",
            "dealer_id",
            "owner_name",
            "phone",
            "model",
            "device_id",
            "network_name",
            "connection_status",
            "last_connection",
            "days_offline"
        ]

        df = df[columnas_finales]

        return df

    # NETWORK NAME ====================================================================================
    def get_trackers_network_name(self, df_trackers: pd.DataFrame) -> dict:
        """Obtiene el nombre de la red GSM para cada tracker utilizando solicitudes concurrentes de NAVIXY."""

        if df_trackers.empty:
            return {}

        network_map = {}

        # obtener usuarios
        df_users = self.get_users()

        if df_users.empty:
            return {tid: None for tid in df_trackers["tracker_id"]}

        # usuarios activos
        active_users = set(
            df_users.loc[df_users["activated"] == True, "user_id"]
        )

        # agrupar trackers por usuario
        user_groups = {
            user_id: group["tracker_id"].tolist()
            for user_id, group in df_trackers.groupby("user_id")
        }

        # Ejecuta el multihilo para obtener el nombre de la data de cada tracker asociado a usuarios activos, 
        # en este caso realiza 10 procesos a la vez, ajustable según necesidades y límites del API. 
        # Para usuarios inactivos, asigna None directamente sin hacer solicitudes.
        with ThreadPoolExecutor(max_workers=40) as executor:

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

            # BARRA DE CARGA
            if futures:
                for future in tqdm(as_completed(futures), total=len(futures), desc="Consultando NAVIXY"):
                    result = future.result()
                    if result:
                        network_map.update(result)
            else:
                # Barra simulada (feedback visual)
                for _ in tqdm(range(1), desc="Consultando NAVIXY"):
                    tqdm.write("Consultando NAVIXY... (sin datos para procesar)")

        return network_map

    # MULTIPROCESO PARA LOS REQUESTS DE PANEL =================================================================
    def _process_user_networks(self, user_id: int, tracker_ids: list) -> dict:
        """Realiza las solicitudes necesarias para obtener el nombre de la red GSM
        para un grupo de trackers asociados a un usuario específico."""
        
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

    # REQUEST CENTRAL ===============================================================================
    def _post(self, url: str, payload: dict, retries = 4) -> dict | None:
        """Realiza una solicitud POST de NAVIXY con manejo de reintentos y control de rate limit."""

        for attempt in range(retries):
            try:
                self.rate_limiter.wait()
                response = self.session.post( url, data = payload, timeout = 15 )
                return response.json()

            except Exception as e:
                print(f"Error desconocido: {e}")
                self.session.close()

        return None
