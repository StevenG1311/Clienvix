import sys
import json
from pathlib import Path

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
                "SEGURITY": ""
            },
            "URLS": {
                "API": "https://api.navixy.com/v2",
                "PANEL_AUTH": "https://api.navixy.com/v2/panel/account/auth",
                "USER_LIST": "https://api.navixy.com/v2/panel/user/list",
                "TRACKER_LIST": "https://panel.navixy.com/api-v2/panel/tracker/list"
            }
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_default, f, indent=4)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)