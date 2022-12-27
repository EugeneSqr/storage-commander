from requests.exceptions import RequestException

from storcom.base_storage import BaseStorage, StorageInteractionError
from storcom.cx_auth import CxAuth

class CxStorage(BaseStorage):
    def __init__(self, config, context):
        self._storage_url, self._token = config
        self._container_sid = context.user

    def file_details(self, file_id):
        try:
            return self._make_request('GET', f'{self._get_files_base_url()}/{file_id}').text
        except RequestException as e:
            raise StorageInteractionError(f"Can't get cx file details for {file_id}") from e

    def delete_file(self, file_id):
        try:
            return self._make_request('DELETE', f'{self._get_files_base_url()}/{file_id}')
        except RequestException as e:
            raise StorageInteractionError(f"Can't delete cx file {file_id}") from e

    @property
    def _tabular_headers(self):
        return [
            'file_sid',
            'name',
            'type',
            'mime_type',
            'file_bytes',
            'content_duration',
            'parent_file_sid',
            'date_modified',
        ]

    def _request_files_list(self):
        try:
            return self._make_request('GET',
                                      self._get_files_base_url(),
                                      params={
                                          'filter': f'container_sid eq {self._container_sid}',
                                      })
        except RequestException as e:
            raise StorageInteractionError("Can't get list of files.") from e

    def _make_request(self, method, url, **kwargs):
        return BaseStorage._make_request(method, url, auth=CxAuth(self._token), **kwargs)

    def _get_files_base_url(self):
        return f'{self._storage_url}/core/v2/storage/files'
