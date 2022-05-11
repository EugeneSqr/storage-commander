import requests
from requests.exceptions import RequestException
from requests.auth import AuthBase
from base_storage import BaseStorage, StorageInteractionError

_TIMEOUT = 10
_TABULAR_HEADERS = ['id', 'name', 'batch', 'purpose', 'threshold_include', 'date_changed']

class FccStorage(BaseStorage):
    def __init__(self, context):
        self._storage_url, self._token = BaseStorage._read_config(context)
        self._owner = context.user

    def file_details(self, file_id):
        try:
            return self._make_request('GET', f'{self._storage_url}/files/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get file details for {file_id}") from e

    def list_files(self):
        return self._request_files_list().text

    def list_files_tabular(self):
        response = self._request_files_list()
        try:
            files_list = response.json()['items']
        except Exception as e:
            raise StorageInteractionError('Invalid file list JSON.') from e

        return [_extract_file_values(f, _TABULAR_HEADERS) for f in files_list], _TABULAR_HEADERS

    def delete_file(self, file_id):
        try:
            return self._make_request('DELETE', f'{self._storage_url}/files/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete file {file_id}") from e

    def _request_files_list(self):
        try:
            response = self._make_request('GET',
                                          f'{self._storage_url}/files',
                                          params={
                                              'ordering': '-date_changed',
                                              **self._owner_param(),
                                          })
            response.raise_for_status()
            return response
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

    def _make_request(self, method, url, **kwargs):
        response = requests.request(
            method, url, auth=_CxAuth(self._token), timeout=_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response

    def _owner_param(self):
        return {'owner': self._owner} if self._owner else {}

def _extract_file_values(file, headers):
    return [file.get(header, '') for header in headers]

class _CxAuth(AuthBase):
    def __init__(self, token):
        self._token = token

    def __call__(self, request):
        request.headers['Authorization'] = f'Bearer {self._token}'
        return request
