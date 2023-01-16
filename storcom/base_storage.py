from abc import ABCMeta, abstractmethod

import requests

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
    def _make_request(method, url, **kwargs):
        response = requests.request(method, url, timeout=_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response

class StorageInteractionError(Exception):
    pass
