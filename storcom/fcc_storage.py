from requests.exceptions import RequestException

from storcom.base_storage import BaseStorage, StorageInteractionError
from storcom.cx_auth import CxAuth

class FccStorage(BaseStorage):
    def __init__(self, context):
        self._storage_url, self._token = BaseStorage._read_config(context)
        self._owner = context.user

    def file_details(self, file_id):
        try:
            return self._make_request('GET', f'{self._storage_url}/files/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get fcc file details for {file_id}") from e

    def delete_file(self, file_id):
        try:
            return self._make_request('DELETE', f'{self._storage_url}/files/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete fcc file {file_id}") from e

    @property
    def _tabular_headers(self):
        return [
            'id',
            'name',
            'batch',
            'purpose',
            'parent_file_id',
            'threshold_include',
            'date_changed',
        ]

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

    def _make_request(self, method, url, **kwargs):
        return BaseStorage._make_request(method, url, auth=CxAuth(self._token), **kwargs)

    def _owner_param(self):
        return {'owner': self._owner} if self._owner else {}
