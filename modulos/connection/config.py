import sys
import json
from pathlib import Path

# ==================================================================================================
# CONFIGURACIÓN Y CONEXIÓN A NAVIXY 
# ==================================================================================================
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]

CONFIG_PATH = BASE_DIR / "config.json"

# VERIFICAR EXISTENCIA DE ARCHVIO DE CONFIGURACIÓN ================================================
def j_config():
    """Este metodo verifica si existe el archivo json que tendra la configuracion 
    y los endpoint desde la cual se estrae la información del api,
    en caso no existir este los crea con las configuraciones en blanco"""

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
                "USER_HASH":"https://api.navixy.com/v2/panel/user/session/create",
                "TRACKER_LIST": "https://panel.navixy.com/api-v2/panel/tracker/list",
                "TRACKER_STATES":"https://api.navixy.com/v2/tracker/get_states"
            },
            "RUTA": ""
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_default, f, indent=4)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

