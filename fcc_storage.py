import requests
from requests.exceptions import RequestException
from requests.auth import AuthBase
from base_storage import BaseStorage, StorageInitError, StorageInteractionError
from config import config

_TIMEOUT = 10

class FccStorage(BaseStorage):
    def __init__(self, context):
        self._storage_url, self._token = FccStorage._read_config(context)
        self._owner = context.user

    def file_details(self, file_id):
        # TODO: implement me
        raise NotImplemented()

    def list_files(self):
        try:
            response = requests.get(f'{self._storage_url}/files',
                                    params=self._params(),
                                    auth=_CxAuth(self._token),
                                    timeout=_TIMEOUT)
            response.raise_for_status()
            return response.text
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

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

    def _params(self):
        params = {}
        if self._owner:
            params['owner'] = self._owner
        return params

class _CxAuth(AuthBase):
    def __init__(self, token):
        self._token = token

    def __call__(self, request):
        request.headers['Authorization'] = f'Bearer {self._token}'
        return request
