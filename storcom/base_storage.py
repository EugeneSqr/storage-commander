from abc import ABCMeta, abstractmethod

import requests

from config import config

_TIMEOUT = 10

class BaseStorage():
    __metaclass__ = ABCMeta

    @abstractmethod
    def file_details(self, file_id):
        pass

    @abstractmethod
    def delete_file(self, file_id):
        pass

    def list_files(self):
        return self._request_files_list().text

    def list_files_tabular(self):
        response = self._request_files_list()
        try:
            files = response.json()['items']
        except Exception as e:
            raise StorageInteractionError('Invalid file list JSON.') from e

        headers = self._tabular_headers
        return [BaseStorage._extract_file_values(f, headers) for f in files], headers

    @property
    @abstractmethod
    def _tabular_headers(self):
        pass

    @abstractmethod
    def _request_files_list(self):
        pass

    @staticmethod
    def _extract_file_values(file, headers):
        return [file.get(header, '') for header in headers]

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

    @staticmethod
    def _make_request(method, url, **kwargs):
        response = requests.request(method, url, timeout=_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response

class StorageInitError(Exception):
    pass

class StorageInteractionError(Exception):
    pass
