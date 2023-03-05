from os import environ as env
from pathlib import Path
from typing import Dict, Any, Tuple, TYPE_CHECKING

import tomli

if TYPE_CHECKING:
    from storcom.context import Context

StorageConfig = Tuple[str, str]

def get_or_create_config_directory() -> Path:
    config_directory = Path(env.get('STORCOM_HOME') or _get_standard_config_directory())
    config_directory.mkdir(parents=True, exist_ok=True)
    return config_directory

def read_storage_config(context: 'Context') -> StorageConfig:
    config = _read_decode_config()
    if context.environment not in config:
        raise ConfigError(f'No config for environment: {context.environment}')
    if context.storage not in config[context.environment]:
        raise ConfigError(f'No config for storage: {context.storage}')
    storage_config = config[context.environment][context.storage]
    storage_url = storage_config.get('storage_url')
    if not storage_url:
        raise ConfigError(f'No storage_url for storage {context.storage}')
    if not context.service:
        raise ConfigError(f'No service for storage: {context.storage}')
    tokens = storage_config.get('tokens') or {}
    service_token = tokens.get(context.service)
    if not service_token:
        raise ConfigError(f'Storage token missing for service: {context.service}')
    return storage_url, service_token

def read_shortcuts() -> Dict[str, str]:
    return _read_decode_config().get('shortcuts', {})

def _read_decode_config() -> Dict[str, Any]:
    config_file_path = get_or_create_config_directory() / 'config.toml'
    try:
        with open(config_file_path, 'rb') as f:
            return tomli.load(f)
    except IOError as e:
        raise ConfigError(f'Unable to read {config_file_path}: {e}') from e
    except tomli.TOMLDecodeError as e:
        raise ConfigError(f'Unable to decode {config_file_path}: {e}') from e

def _get_standard_config_directory() -> Path:
    home_directory = env.get('HOME')
    assert home_directory is not None
    config_directory = Path(env.get('XDG_CONFIG_HOME') or Path(home_directory) / '.config')
    return config_directory / 'storcom'

class ConfigError(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message: str = message
