import tomli

def read():
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
