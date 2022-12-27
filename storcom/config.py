import tomli

def read_storage_config(context):
    config = _read_decode_config()
    if context.environment not in config:
        raise StorageInitError(f'No config for environment: {context.environment}')
    if context.storage not in config[context.environment]:
        raise StorageInitError(f'No config for storage: {context.storage}')
    storage_config = config[context.environment][context.storage]
    storage_url = storage_config.get('storage_url')
    if not storage_url:
        raise StorageInitError(f'No storage_url for storage {context.storage}')
    if not context.service:
        raise StorageInitError(f'No service for storage: {context.storage}')
    tokens = storage_config.get('tokens') or {}
    service_token = tokens.get(context.service)
    if not service_token:
        raise StorageInitError(f'Storage token missing for service: {context.service}')
    return storage_url, service_token

def read_contexts():
    try:
        contexts = _read_decode_config().get('contexts', {})
    except StorageInitError:
        contexts = {}
    return contexts

def _read_decode_config():
    config_file_path = 'config.toml'
    try:
        with open(config_file_path, 'rb') as f:
            return tomli.load(f)
    except IOError as e:
        raise StorageInitError(f'Unable to read {config_file_path}: {e}') from e
    except tomli.TOMLDecodeError as e:
        raise StorageInitError(f'Unable to decode {config_file_path}: {e}') from e

# TODO: rename to something related to config
class StorageInitError(Exception):
    pass
