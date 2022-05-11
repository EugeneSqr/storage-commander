from abc import ABCMeta, abstractmethod

from config import config

class BaseStorage():
    __metaclass__ = ABCMeta

    @abstractmethod
    def file_details(self, file_id):
        pass

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def list_files_tabular(self):
        pass

    @abstractmethod
    def delete_file(self, file_id):
        pass

    @staticmethod
    def _read_config(context):
        if context.environment not in config:
            raise StorageInitError(f'No config for environment: {context.environment}')
        if context.storage not in config[context.environment]:
            raise StorageInitError(f'No config for storage: {context.storage}')
        storage_config = config[context.environment][context.storage]
        storage_url = storage_config.get('storage_url')
        if not storage_url:
            raise StorageInitError(f'No storage_url configured for storage {context.storage}')
        if not context.service:
            raise StorageInitError(f'No service specified for storage: {context.storage}')
        tokens = storage_config.get('tokens') or {}
        service_token = tokens.get(context.service)
        if not service_token:
            raise StorageInitError(f'Storage token missing for service: {context.service}')
        return storage_url, service_token


class StorageInitError(Exception):
    pass

class StorageInteractionError(Exception):
    pass
