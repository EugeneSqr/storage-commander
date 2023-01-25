from abc import ABCMeta, abstractmethod
from multiprocessing.pool import ThreadPool

import requests
from requests.exceptions import RequestException
from requests.auth import AuthBase


_THREAD_POOL_SIZE = 5
_TIMEOUT = 10


class BaseStorage():
    __metaclass__ = ABCMeta

    @abstractmethod
    def file_details(self, file_id):
        pass

    @abstractmethod
    def delete_files(self, file_ids):
        pass

    def list_files(self):
        return self._request_files_list().text

    def list_files_tabular(self, extra_fields=None):
        return _list_files_tabular(
            self._request_files_list(),
            [*self._tabular_fields_begin, *(extra_fields or []), *self._tabular_fields_end])

    @property
    @abstractmethod
    def _tabular_fields_begin(self):
        pass

    @property
    @abstractmethod
    def _tabular_fields_end(self):
        pass

    @abstractmethod
    def _request_files_list(self):
        pass


class FccStorage(BaseStorage):
    def __init__(self, config, context):
        self._storage_url, self._token = config
        self._owner = context.user

    def file_details(self, file_id):
        try:
            return self._make_request('GET', f'{self._storage_url}/files/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get fcc file details for {file_id}") from e

    def delete_files(self, file_ids):
        ThreadPool(processes=_THREAD_POOL_SIZE).map(self._delete_file, file_ids)

    @property
    def _tabular_fields_begin(self):
        return ['id', 'name', 'batch', 'date_changed']

    @property
    def _tabular_fields_end(self):
        return ['date_changed']

    def _request_files_list(self):
        try:
            return self._make_request('GET',
                                      f'{self._storage_url}/files',
                                      params={
                                          'ordering': '-date_changed',
                                          **self._owner_param(),
                                      })
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

    def _delete_file(self, file_id):
        try:
            self._make_request('DELETE', f'{self._storage_url}/files/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete fcc file {file_id}") from e

    def _make_request(self, method, url, **kwargs):
        return _make_request(method, url, auth=CxAuth(self._token), **kwargs)

    def _owner_param(self):
        return {'owner': self._owner} if self._owner else {}


class CxStorage(BaseStorage):
    def __init__(self, config, context):
        self._storage_url, self._token = config
        self._container_sid = context.user

    def file_details(self, file_id):
        try:
            return self._make_request('GET', f'{self._get_files_base_url()}/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get cx file details for {file_id}") from e

    def delete_files(self, file_ids):
        ThreadPool(processes=_THREAD_POOL_SIZE).map(self._delete_file, file_ids)

    @property
    def _tabular_fields_begin(self):
        return ['file_sid', 'name', 'type', 'mime_type']

    @property
    def _tabular_fields_end(self):
        return ['date_modified']

    def _request_files_list(self):
        try:
            return self._make_request('GET',
                                      self._get_files_base_url(),
                                      params={
                                          'filter': f'container_sid eq {self._container_sid}',
                                      })
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

    def _delete_file(self, file_id):
        try:
            self._make_request('DELETE', f'{self._get_files_base_url()}/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete cx file {file_id}") from e

    def _make_request(self, method, url, **kwargs):
        return _make_request(method, url, auth=CxAuth(self._token), **kwargs)

    def _get_files_base_url(self):
        return f'{self._storage_url}/core/v2/storage/files'


class StorageInteractionError(Exception):
    pass


class CxAuth(AuthBase):
    def __init__(self, token):
        self._token = token

    def __call__(self, request):
        request.headers['Authorization'] = f'Bearer {self._token}'
        return request


def _make_request(method, url, **kwargs):
    response = requests.request(method, url, timeout=_TIMEOUT, **kwargs)
    response.raise_for_status()
    return response

def _list_files_tabular(files_list_response, fields):
    try:
        files = files_list_response.json()['items']
    except Exception as e:
        raise StorageInteractionError('Invalid file list JSON.') from e

    return [_get_tabular_field_values(file, fields) for file in files], fields

def _get_tabular_field_values(file, fields):
    return [file.get(field, '') for field in fields]
