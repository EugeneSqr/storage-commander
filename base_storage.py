from abc import ABCMeta, abstractmethod

class BaseStorage():
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_files(self):
        pass

class StorageInitError(Exception):
    pass

class StorageInteractionError(Exception):
    pass
