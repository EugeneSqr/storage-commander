import sys
from abc import ABCMeta, abstractmethod
from multiprocessing.pool import ThreadPool
from typing import List, Dict, Tuple, Optional, Any

import curlify
import requests
from requests.exceptions import RequestException
from requests.auth import AuthBase

from storcom.context import Context
from storcom.config import StorageConfig

_THREAD_POOL_SIZE = 5
_TIMEOUT = 10

File = Dict[str, str]
TabularFileList = Tuple[List[List[str]], List[str]]

class BaseStorage():
    __metaclass__ = ABCMeta

    def __init__(self, config: StorageConfig, show_curl: bool=False):
        self._storage_url, self._token = config
        self._show_curl = show_curl

    @property
    def filter_field_names(self) -> List[str]:
        return []

    @abstractmethod
    def show_file(self, file_id: str) -> str:
        pass

    @abstractmethod
    def delete_files(self, file_ids: List[str]) -> None:
        pass

    def list_files(self, filter_fields: Dict[str, str]) -> str:
        return self._request_files_list(filter_fields).text

    def list_files_tabular(self,
                           middle_columns: List[str],
                           filter_fields: Dict[str, str]) -> TabularFileList:
        return _list_files_tabular(
            self._request_files_list(filter_fields),
            [*self._leading_columns, *(middle_columns or []), *self._trailing_columns])

    @property
    @abstractmethod
    def _leading_columns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def _trailing_columns(self) -> List[str]:
        pass

    @abstractmethod
    def _request_files_list(self, filter_fields: Dict[str, str]) -> requests.Response:
        pass

    def _make_request(self,
                      method: str,
                      url: str,
                      **kwargs: Optional[Any]) -> requests.Response:
        response = requests.request(method,
                                    url,
                                    allow_redirects=True,
                                    auth=CxAuth(self._token),
                                    timeout=_TIMEOUT,
                                    **kwargs)
        if self._show_curl:
            print(curlify.to_curl(response.request), file=sys.stderr)
        response.raise_for_status()
        return response

class FccStorage(BaseStorage):
    def __init__(self, config: StorageConfig, context: Context, show_curl: bool=False):
        super().__init__(config, show_curl)
        self._owner = context.user

    @property
    def filter_field_names(self) -> List[str]:
        return ['batch']

    def show_file(self, file_id: str) -> str:
        try:
            return self._make_request('GET', f'{self._storage_url}/files/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get fcc file details for {file_id}") from e

    def delete_files(self, file_ids: List[str]) -> None:
        ThreadPool(processes=_THREAD_POOL_SIZE).map(self._delete_file, file_ids)

    @property
    def _leading_columns(self) -> List[str]:
        return ['id', 'name', 'batch', 'date_changed']

    @property
    def _trailing_columns(self) -> List[str]:
        return ['date_changed']

    def _request_files_list(self, filter_fields: Dict[str, str]) -> requests.Response:
        try:
            return self._make_request('GET',
                                      f'{self._storage_url}/files',
                                      params={
                                          'ordering': '-date_changed',
                                          **self._owner_param(),
                                      })
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

    def _delete_file(self, file_id: str) -> None:
        try:
            self._make_request('DELETE', f'{self._storage_url}/files/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete fcc file {file_id}") from e

    def _owner_param(self) -> Dict[str, str]:
        return {'owner': self._owner} if self._owner else {}

class CxStorage(BaseStorage):
    def __init__(self, config: StorageConfig, context: Context, show_curl: bool=False):
        super().__init__(config, show_curl)
        self._container_sid = context.user

    def show_file(self, file_id: str) -> str:
        try:
            return self._make_request('GET', f'{self._get_files_base_url()}/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get cx file details for {file_id}") from e

    def delete_files(self, file_ids: List[str]) -> None:
        ThreadPool(processes=_THREAD_POOL_SIZE).map(self._delete_file, file_ids)

    @property
    def _leading_columns(self) -> List[str]:
        return ['file_sid', 'name', 'type', 'mime_type']

    @property
    def _trailing_columns(self) -> List[str]:
        return ['date_modified']

    def _request_files_list(self, filter_fields: Dict[str, str]) -> requests.Response:
        try:
            return self._make_request('GET',
                                      self._get_files_base_url(),
                                      params={
                                          'filter': f'container_sid eq {self._container_sid}',
                                      })
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

    def _delete_file(self, file_id: str) -> None:
        try:
            self._make_request('DELETE', f'{self._get_files_base_url()}/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete cx file {file_id}") from e

    def _get_files_base_url(self) -> str:
        return f'{self._storage_url}/core/v2/storage/files'

class StorageInteractionError(Exception):
    pass

class CxAuth(AuthBase):
    def __init__(self, token: str):
        self._token = token

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        request.headers['Authorization'] = f'Bearer {self._token}'
        return request

def _list_files_tabular(files_list_response: requests.Response,
                        fields: List[str]) -> TabularFileList:
    try:
        files: List[File] = files_list_response.json()['items']
    except Exception as e:
        raise StorageInteractionError('Invalid file list JSON.') from e

    return [_get_tabular_field_values(file, fields) for file in files], fields

def _get_tabular_field_values(file: File, fields: List[str]) -> List[str]:
    return [file.get(field, '') for field in fields]
