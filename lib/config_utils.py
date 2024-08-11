# coding: utf8
import os
import sys
import json
from pathlib import Path

from cryptography.fernet import Fernet


def path_not_exist(path: str | Path) -> bool:
    """
    判断目标路径是否存在
    如果参数为空或者 None，亦认为不存在

    :param path: 目标路径
    :return:
    """
    if isinstance(path, str):
        return len(path) == 0 or not Path(path).exists()
    elif isinstance(path, Path):
        return not path.exists()
    else:
        return True


def get_data_dir() -> str:
    plat = sys.platform
    if plat == "win32":
        data_dir = os.path.expandvars("%appdata%")
    elif plat == "darwin":
        data_dir = os.path.expanduser("~/Library/Application Support")
    else:
        raise OSError("Unsupported platform")
    return data_dir


def get_app_dir(org_name: str, app_name: str) -> Path:
    data_dir = get_data_dir()
    app_dir = Path(data_dir, org_name, app_name)
    if not app_dir.exists():
        app_dir.mkdir(parents=True, exist_ok=True)

    return app_dir


def get_config_path(org_name: str, app_name: str) -> Path:
    app_dir = get_app_dir(org_name, app_name)
    return Path(app_dir, "config.json")


def read_config(org_name: str, app_name: str) -> dict:
    config = {
        "button_min_width": 120,
        "last_db_path": "",
        "last_open_path": "../",
        "loaded_memory": {}
    }
    config_path = get_config_path(org_name, app_name)
    if not config_path.exists():
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=4), encoding="utf-8")
        return config
    else:
        exist_config = json.loads(config_path.read_text(encoding="utf-8"))
        for key, value in config.items():
            if key not in exist_config:
                exist_config[key] = value
        return exist_config


def write_config(config: dict, org_name: str, app_name: str):
    config_path = get_config_path(org_name, app_name)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=4), encoding="utf-8")


def get_default_db_path(config: dict, org_name: str, app_name: str) -> str:
    if path_not_exist(config["last_db_path"]):
        app_dir = get_app_dir(org_name, app_name)
        return str(app_dir / f"default.db")
    return config["last_db_path"]


def get_secrets_path(org_name: str, app_name: str) -> str:
    app_dir = get_app_dir(org_name, app_name)
    return str(app_dir / "secrets.db")


def get_or_generate_key(db_name: str, org_name: str, app_name: str) -> bytes:
    app_dir = get_app_dir(org_name, app_name)
    name = Path(db_name).name
    key_path = app_dir / f"{name}.key"
    if key_path.exists():
        key = key_path.read_bytes()
    else:
        key = Fernet.generate_key()
        key_path.write_bytes(key)
    return key
