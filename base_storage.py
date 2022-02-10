from abc import ABCMeta, abstractmethod

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

class StorageInitError(Exception):
    pass

class StorageInteractionError(Exception):
    pass
